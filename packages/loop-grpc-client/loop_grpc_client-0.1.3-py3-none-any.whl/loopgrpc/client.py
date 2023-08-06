from .common import BaseClient, looprpc
from .errors import handle_rpc_errors

from loopgrpc.swapclient import SwapClientRPC
from loopgrpc.debug import DebugRPC


class LoopClient(SwapClientRPC, DebugRPC):
    pass

def cli():
    import os
    import code
    # from pathlib import Path
    # credential_path = os.getenv("LOOP_CRED_PATH", None)
    # if credential_path == None:
    #     credential_path = Path("/home/skorn/.loop/mainnet")
    # else:
    #     credential_path = Path(credential_path)

    # loop_ip = os.getenv("LOOP_IP")
    # loop_port = os.getenv("LOOP_PORT")

    # mac = str(credential_path.joinpath("loop.macaroon").absolute())
    # tls = str(credential_path.joinpath("tls.cert").absolute())

    # pool_ip_port = f"{loop_ip}:{loop_port}"


    loop = LoopClient(
        # pool_ip_port,
        # macaroon_filepath=mac,
        # cert_filepath=tls,
        # no_tls=True
    )

    code.interact(local=dict(globals(), **locals()))  