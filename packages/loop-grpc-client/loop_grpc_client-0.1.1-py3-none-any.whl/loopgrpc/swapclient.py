from .common import BaseClient, looprpc
from .errors import handle_rpc_errors


class SwapClientRPC(BaseClient):
    @handle_rpc_errors
    def get_liquidity_params(self):
        """GetLiquidityParams"""
        request = looprpc.GetLiquidityParamsRequest()
        response = self._client_stub.GetLiquidityParams(request)
        return response


    @handle_rpc_errors
    def get_loop_in_quote(self, amt, conf_target, external_htlc=False, **kwargs):
        """GetLoopInQuote"""
        request = looprpc.QuoteRequest(
            amt=amt,
            conf_target=conf_target,
            external_htlc=external_htlc,
            **kwargs
        )
        response = self._client_stub.GetLoopInQuote(request)
        return response

    @handle_rpc_errors
    def get_loop_in_terms(self):
        """GetLoopInTerms"""
        request = looprpc.TermsRequest()
        response = self._client_stub.GetLoopInTerms(request)
        return response

    @handle_rpc_errors
    def get_lsat_tokens(self):
        """GetLsatTokens"""
        request = looprpc.TokensRequest()
        response = self._client_stub.GetLsatTokens(request)
        return response

    @handle_rpc_errors
    def list_swaps(self):
        """ListSwaps"""
        request = looprpc.ListSwapsRequest()
        response = self._client_stub.ListSwaps(request)
        return response

    @handle_rpc_errors
    def loop_in(self, amt, conf_target, external_htlc=False, **kwargs):
        """LoopIn"""
        request = looprpc.LoopInRequest(
            amt=amt,
            conf_target=conf_target,
            external_htlc=external_htlc,
            **kwargs
        )
        response = self._client_stub.LoopIn(request)
        return response

    @handle_rpc_errors
    def loop_out(self, **kwargs):
        """LoopOut"""
        request = looprpc.LoopOutRequest()
        response = self._client_stub.LoopOut(request)
        return response

    @handle_rpc_errors
    def loop_out_quote(self, **kwargs):
        """LoopOutQuote"""
        request = looprpc.QuoteRequest(**kwargs)
        response = self._client_stub.LoopOutQuote(request)
        return response

    @handle_rpc_errors
    def loop_out_terms(self):
        """LoopOutTerms"""
        request = looprpc.TermsRequest()
        response = self._client_stub.LoopOutTerms(request)
        return response

    @handle_rpc_errors
    def monitor(self):
        """Monitor"""
        request = looprpc.MonitorRequest()
        response = self._client_stub.Monitor(request)
        return response

    @handle_rpc_errors
    def probe(self, **kwargs):
        """Probe"""
        request = looprpc.ProbeRequest(**kwargs)
        response = self._client_stub.Probe(request)
        return response

    @handle_rpc_errors
    def set_liquidity_params(self):
        """SetLiquidityParams"""
        return "not implemented"
        request = looprpc.GetLiquidityParamsRequest()
        response = self._client_stub.GetLiquidityParams(request)
        return response

    @handle_rpc_errors
    def suggest_swaps(self):
        """SuggestSwaps"""
        request = looprpc.SuggestSwapsRequest()
        response = self._client_stub.SuggestSwaps(request)
        return response


    @handle_rpc_errors
    def swap_info(self, id):
        """SwapInfo"""
        request = looprpc.SwapInfoRequest(id=id)
        response = self._client_stub.SwapInfo(request)
        return response
