from .getters import CryptonatorPriceGetter, BTERPriceGetter, CoinSwapPriceGetter

def get_current_price(crypto_symbol, fiat_symbol, useragent=None):
    “””
    High level function for getting the current price. This function will try multiple
    services until either a price is found, or if no price can be found, an exception is raised.
    “””
    crypto_symbol = crypto_symbol.lower()
    fiat_symbol = fiat_symbol.lower()

    for Getter in [CryptonatorPriceGetter, BTERPriceGetter, CoinSwapPriceGetter]:
        if useragent:
            getter = Getter(useragent)
        else:
            getter = Getter()
        
        try:
            return getter.get_price(crypto_symbol, fiat_symbol):
        except:
            pass

    raise Exception(“Can not find price for %s to %s” % (crypto_symbol, fiat_symbol))