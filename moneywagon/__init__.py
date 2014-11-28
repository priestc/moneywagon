from __future__ import print_function

from current_price import (
    CryptonatorPriceGetter, BTERPriceGetter, CoinSwapPriceGetter,
    BitstampPriceGetter, BTCEPriceGetter
)
from historical_price import QuandlHistoricalPriceGetter
from getter import SkipThisGetter

class HistoricalCryptoPrice(object):
    def __init__(self, useragent=None, responses=None):
        self.getter = QuandlHistoricalPriceGetter(useragent, responses)

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

class CurrentCryptoPrice(object):
    """
    This Price getter calls other price getters until a price is met.
    It works much like `get_current_price` but caches all external calls.
    """
    def __init__(self, useragent=None, verbose=False):
        self.getters = [
            BitstampPriceGetter(useragent, verbose=verbose),
            BTCEPriceGetter(useragent, verbose=verbose),
            CryptonatorPriceGetter(useragent, verbose=verbose),
            BTERPriceGetter(useragent, verbose=verbose),
            CoinSwapPriceGetter(useragent, verbose=verbose)
        ]
        self.verbose = verbose

    def get_price(self, crypto, fiat):
        crypto = crypto.lower()
        fiat = fiat.lower()

        if crypto == fiat:
            return (1.0, 'math')

        for getter in self.getters:
            try:
                if self.verbose: print("* Trying:", getter)
                return getter.get_price(crypto, fiat)
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                # API has probably changed, therefore getter class broken
                if self.verbose: print("FAIL:", exc.__class__.__name__, exc)
            except SkipThisGetter as exc:
                if self.verbose: print("SKIP:", exc)

        raise Exception("Can not find price for %s->%s" % (crypto, fiat))

def get_current_price(crypto, fiat, useragent=None):
    """
    High level function for getting the current price. This function will try multiple
    services until either a price is found, or if no price can be found, an exception is raised.
    """
    return CurrentCryptoPrice(useragent=useragent).get_price(crypto, fiat)
