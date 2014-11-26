from current_price import CryptonatorPriceGetter, BTERPriceGetter, CoinSwapPriceGetter
from historical_price import QuandlHistoricalPriceGetter

class CurrentCryptoPriceGetter(object):
    """
    This Price getter calls other price getters until a price is met.
    It works much like `get_current_price` but caches all external calls.
    """
    def __init__(self, useragent=None):
        self.getters = [
            CryptonatorPriceGetter(useragent),
            BTERPriceGetter(useragent),
            CoinSwapPriceGetter(useragent)
        ]

    def get_price(self, crypto_symbol, fiat_symbol):
        crypto_symbol = crypto_symbol.lower()
        fiat_symbol = fiat_symbol.lower()

        if crypto_symbol == fiat_symbol:
            return (1.0, 'math')

        for getter in self.getters:
            try:
                return getter.get_price(crypto_symbol, fiat_symbol)
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                # API has probably changed, therefore getter class broken
                pass

        raise Exception("Can not find price for %s to %s" % (crypto_symbol, fiat_symbol))

def get_current_price(crypto_symbol, fiat_symbol, useragent=None):
    """
    High level function for getting the current price. This function will try multiple
    services until either a price is found, or if no price can be found, an exception is raised.
    """
    return CurrentCryptoPriceGetter(useragent).get_price(crypto_symbol, fiat_symbol)
