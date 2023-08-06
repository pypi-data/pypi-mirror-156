import binascii
import platform
import os
from pathlib import Path
import grpc
from loopgrpc.compiled import (
    client_pb2 as looprpc,
    client_pb2_grpc as clientstub,
)


system = platform.system().lower()

if system == "linux":
    TLS_FILEPATH = os.path.expanduser("~/.lnd/tls.cert")
    ADMIN_MACAROON_BASE_FILEPATH = "~/.lnd/data/chain/bitcoin/{}/admin.macaroon"
    READ_ONLY_MACAROON_BASE_FILEPATH = "~/.lnd/data/chain/bitcoin/{}/readonly.macaroon"
elif system == "darwin":
    TLS_FILEPATH = os.path.expanduser("~/Library/Application Support/Lnd/tls.cert")
    ADMIN_MACAROON_BASE_FILEPATH = (
        "~/Library/Application Support/Lnd/data/chain/bitcoin/{}/admin.macaroon"
    )
    READ_ONLY_MACAROON_BASE_FILEPATH = (
        "~/Library/Application Support/Lnd/data/chain/bitcoin/{}/readonly.macaroon"
    )
elif system == "windows":
    TLS_FILEPATH = os.path.join(
        os.path.expanduser("~"), "AppData", "Local", "Lnd", "tls.cert"
    )
    ADMIN_MACAROON_BASE_FILEPATH = os.path.join(
        os.path.expanduser("~"),
        "AppData",
        "Local",
        "Lnd",
        "data",
        "chain",
        "bitcoin",
        "mainnet",
        "admin.macaroon",
    )
    READ_ONLY_MACAROON_BASE_FILEPATH = os.path.join(
        os.path.expanduser("~"),
        "AppData",
        "Local",
        "Lnd",
        "data",
        "chain",
        "bitcoin",
        "mainnet",
        "readonly.macaroon",
    )
else:
    raise SystemError("Unrecognized system")


# Due to updated ECDSA generated tls.cert we need to let gprc know that
# we need to use that cipher suite otherwise there will be a handhsake
# error when we communicate with the lnd rpc server.
os.environ["GRPC_SSL_CIPHER_SUITES"] = "HIGH+ECDSA"


def get_cert(filepath=None):
    """Read in tls.cert from file

    Note: tls files need to be read in byte mode as of grpc 1.8.2
          https://github.com/grpc/grpc/issues/13866
    """
    with open(filepath, "rb") as f:
        cert = f.read()
    return cert


def get_macaroon(network="mainnet", filepath=None):
    """Read and decode macaroon from file

    The macaroon is decoded into a hex string and returned.
    """
    # if filepath is None:
    #     if admin:
    #         filepath = os.path.expanduser(ADMIN_MACAROON_BASE_FILEPATH.format(network))
    #     else:
    #         filepath = os.path.expanduser(
    #             READ_ONLY_MACAROON_BASE_FILEPATH.format(network)
    #         )

    with open(filepath, "rb") as f:
        macaroon_bytes = f.read()
    return binascii.hexlify(macaroon_bytes).decode()


def generate_credentials(cert, macaroon):
    """Create composite channel credentials using cert and macaroon metadata"""
    # create cert credentials from the tls.cert file
    cert_creds = grpc.ssl_channel_credentials(cert)

    # build meta data credentials
    metadata_plugin = MacaroonMetadataPlugin(macaroon)
    auth_creds = grpc.metadata_call_credentials(metadata_plugin)

    # combine the cert credentials and the macaroon auth credentials
    # such that every call is properly encrypted and authenticated
    return grpc.composite_channel_credentials(cert_creds, auth_creds)


class MacaroonMetadataPlugin(grpc.AuthMetadataPlugin):
    """Metadata plugin to include macaroon in metadata of each RPC request"""

    def __init__(self, macaroon):
        self.macaroon = macaroon

    def __call__(self, context, callback):
        callback([("macaroon", self.macaroon)], None)


class BaseClient(object):
    grpc_module = grpc

    def __init__(
        self,
        ip_address=None,
        network="mainnet",
        cert=None,
        cert_filepath=None,
        macaroon=None,
        macaroon_filepath=None,
    ):
        credential_path = os.getenv("LOOP_CRED_PATH", None)
        root_dir = os.getenv("LOOP_ROOT_DIR", None)
        network = os.getenv("LOOP_NETWORK", None)
        node_ip = os.getenv("LOOP_IP")
        node_port = os.getenv("LOOP_PORT")
        # Handle either passing in credentials_paths, or environment variable paths

        # IF credential_path
        # ELIF root_dir + network
        # ELSE use passed in macaroon_filepath and cert_filepath
        # ELSE use macaroon, and cert

        if credential_path:
            credential_path = Path(credential_path)
            macaroon_filepath = str(credential_path.joinpath("loop.macaroon").absolute())
            cert_filepath = str(credential_path.joinpath("tls.cert").absolute())

        elif root_dir and network:
            macaroon_filepath = str(root_dir.joinpath(f"{network}/loop.macaroon").absolute())
            cert_filepath = str(root_dir.joinpath(f"{network}/tls.cert").absolute())

        elif (macaroon_filepath and cert_filepath) or (macaroon and cert):
            pass
        
        else:
            print("Missing credentials!")
            sys.exit(1)



        if ip_address is None:
            ip_address = f"{node_ip}:{node_port}"

        # handle passing in credentials and cert directly
        if macaroon is None:
            macaroon = get_macaroon(filepath=macaroon_filepath)

        if cert is None:
            cert = get_cert(cert_filepath)

        self._credentials = generate_credentials(cert, macaroon)
        self.ip_address = ip_address

    @property
    def _client_stub(self):
        """Create a ln_stub dynamically to ensure channel freshness

        If we make a call to the Lightning RPC service when the wallet
        is locked or the server is down we will get back an RPCError with
        StatusCode.UNAVAILABLE which will make the channel unusable.
        To ensure the channel is usable we create a new one for each request.
        """
        channel = self.grpc_module.secure_channel(
            self.ip_address,
            self._credentials,
            options=[("grpc.max_receive_message_length", 1024 * 1024)],
        )
        return clientstub.SwapClientStub(channel)

