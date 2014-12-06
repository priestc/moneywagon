from __future__ import print_function

from .services import *
from .core import AutoFallback
from .historical_price import Quandl

def get_current_price(crypto, fiat):
    """
    High level function for getting the current price. This function will try multiple
    services until either a price is found, or if no price can be found, an exception is raised.
    """
    return CurrentPrice().get_price(crypto, fiat)

class HistoricalTransactions(AutoFallback):
    service_classes = [
        Blockr,
        ChainSo,
        NXTPortal,
        ReddcoinCom,
        BitpayInsight,
    ]
    method_name = 'get_transactions'

    def get_transactions(self, crypto, address):
        crypto = crypto.lower()
        return self._try_each_service(crypto, address)

    def no_service_msg(self, crypto, address):
        return "Could not get transactions for: %s" % crypto

class CurrentPrice(AutoFallback):
    service_classes = [
        Bitstamp,
        BTCE,
        Cryptonator,
        BTER,
        CoinSwap
    ]
    method_name = 'get_price'

    def get_price(self, crypto, fiat):
        crypto = crypto.lower()
        fiat = fiat.lower()

        if crypto == fiat:
            return (1.0, 'math')

        return self._try_each_service(crypto, fiat)

    def no_service_msg(self, crypto, fiat):
        return "Can not find price for %s->%s" % (crypto, fiat)

class AddressBalance(AutoFallback):
    service_classes = [
        BlockChainInfo,
        BitEasy,
        DogeChainInfo,
        VertcoinOrg,
        FeathercoinCom,
        NXTPortal,
        Blockr,
        CryptoID,
        BlockCypher,
        CryptapUS,
        ReddcoinCom
    ]
    method_name = "get_balance"

    def get_balance(self, crypto, address):
        crypto = crypto.lower()
        return self._try_each_service(crypto, address)

    def no_service_msg(self, crypto, address):
        return "Could not get address balance for: %s" % crypto



class HistoricalPrice(object):
    def __init__(self, responses=None, verbose=False):
        self.service = Quandl(responses, verbose=verbose)

    def get_historical(self, crypto, fiat, at_time):
        crypto = crypto.lower()
        fiat = fiat.lower()

        if crypto != 'btc' and fiat != 'btc':
            # two external requests and some math is going to be needed.
            from_btc, source1, date1 = self.service.get_historical(crypto, 'btc', at_time)
            to_altcoin, source2, date2 = self.service.get_historical('btc', fiat, at_time)
            return (from_btc * to_altcoin), "%s x %s" % (source1, source2), date1
        else:
            return self.service.get_historical(crypto, fiat, at_time)

    @property
    def responses(self):
        return self.service.responses
