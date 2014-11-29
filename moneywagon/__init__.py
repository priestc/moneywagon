from __future__ import print_function

from .current_price import (
    CryptonatorCurrentPrice, BTERCurrentPrice, CoinSwapCurrentPrice,
    BitstampCurrentPrice, BTCECurrentPrice
)
from .historical_price import QuandlHistoricalPrice
from .historical_transactions import BlockrHistoricalTransaction, ChainSoHistoricalTransaction
from .fetcher import SkipThisFetcher

class AutoFallback(object):
    """
    Calls a succession of getters until one returns a value.
    """

    fetcher_classes = []
    method_name = None

    def __init__(self, useragent=None, verbose=False, responses=None):
        self.getters = []
        for Fetcher in self.fetcher_classes:
            self.getters.append(
                Fetcher(useragent, verbose=verbose, responses=responses)
            )

        self.verbose = verbose

    def _get(self, *args, **kwargs):
        for getter in self.getters:
            try:
                if self.verbose: print("* Trying:", getter)
                return getattr(getter, self.method_name)(*args, **kwargs)
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                # API has probably changed, therefore getter class broken
                if self.verbose: print("FAIL:", exc.__class__.__name__, exc)
            except SkipThisFetcher as exc:
                if self.verbose: print("SKIP:", exc)

        return self.no_return_value(*args, **kwargs)

    def no_return_value(self, *args, **kwargs):
        """
        This function is called when all fetchers have been tried and no value
        can be returned. It much take the same args and kwargs as in the method
        spefified in `self.method_name`. This functin can return a number or
        (more reasonably) raise an exception.
        """
        pass

class HistoricalTransactions(AutoFallback):
    fetcher_classes = [BlockrHistoricalTransaction, ChainSoHistoricalTransaction]
    method_name = 'get_transactions'

    def get_transactions(self, crypto, address):
        crypto = crypto.lower()
        return self._get(crypto, address)

    def no_return_value(self, crypto, address):
        raise Exception("Unable to get transaction for %s" % address)


class CurrentPrice(AutoFallback):
    """
    This Price getter calls other price getters until a price is met.
    It works much like `get_current_price` but caches all external calls.
    """
    fetcher_classes = [
        BitstampCurrentPrice, BTCECurrentPrice, CryptonatorCurrentPrice,
        BTERCurrentPrice, CoinSwapCurrentPrice
    ]
    method_name = 'get_price'

    def get_price(self, crypto, fiat):
        crypto = crypto.lower()
        fiat = fiat.lower()

        if crypto == fiat:
            return (1.0, 'math')

        return self._get(crypto, fiat)

    def no_return_value(self, crypto, fiat):
        raise Exception("Can not find price for %s->%s" % (crypto, fiat))


class HistoricalPrice(object):
    def __init__(self, useragent=None, responses=None):
        self.getter = QuandlHistoricalPrice(useragent, responses)

    def get_historical(self, crypto, fiat, at_time):
        crypto = crypto.lower()
        fiat = fiat.lower()

        if crypto != 'btc' and fiat != 'btc':
            # two external requests and some math is going to be needed.
            from_btc, source1, date1 = self.getter.get_historical(crypto, 'btc', at_time)
            to_altcoin, source2, date2 = self.getter.get_historical('btc', fiat, at_time)
            return (from_btc * to_altcoin), "%s x %s" % (source1, source2), date1
        else:
            return self.getter.get_historical(crypto, fiat, at_time)

    @property
    def responses(self):
        return self.getter.responses


def get_current_price(crypto, fiat, useragent=None):
    """
    High level function for getting the current price. This function will try multiple
    services until either a price is found, or if no price can be found, an exception is raised.
    """
    return CurrentPrice(useragent=useragent).get_price(crypto, fiat)
