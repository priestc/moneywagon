import requests

class PriceGetter(object):
    """
    All getters should subclass this class, and implement their own `get_price` function
    """

    def __init__(self, useragent=None):
        self.useragent = useragent or 'pycryptoprices 1.0'
        self.responses = {} # for caching

    def fetch_url(self, *args, **kwargs):
        """
        Wrapper for requests.get with useragent automatically set.
        """
        url = args[0]
        if url in self.responses.keys():
            return self.responses[url] # return from cache if its there

        headers = kwargs.pop('headers', None)
        custom = {'User-Agent': self.useragent}
        if headers:
            headers.update(custom)
            kwargs['headers'] = headers
        else:
            kwargs['headers'] = custom

        response = requests.get(*args, **kwargs)
        self.responses[url] = response # cache for later
        return response

    def get_price(self, crypto_symbol, fiat_symbol):
        """
        Makes call to external service, and returns the price for given
        fiat/crypto pair. Returns two item tuple: (price, best_market)
        """
        pass


class OldCryptoCoinChartsPriceGetter(PriceGetter):
    """
    Using raw rest API (looks to be currently broken)
    """
    def get_price(self, crypto_symbol, fiat_symbol):
        url = "http://api.cryptocoincharts.info/tradingPairs/%s_%s" % (
            crypto_symbol, fiat_symbol
        )
        response = self.fetch_url(url).json()
        return float(response['price'] or 0), response['best_market']


class CryptoCoinChartsPriceGetter(PriceGetter):
    """
    Using fancy API client library (currently broken)
    """
    def get_price(self, crypto_symbol, fiat_symbol):
        from CryptoCoinChartsApi import API as CCCAPI
        api = CCCAPI()
        tradingpair = api.tradingpair("%s_%s" % (crypto_symbol, fiat_symbol))
        return tradingpair.price, tradingpair.best_market


class BTERPriceGetter(PriceGetter):
    def get_price(self, crypto_symbol, fiat_symbol):
        url_template = "http://data.bter.com/api/1/ticker/%s_%s"
        url = url_template % (crypto_symbol, fiat_symbol)

        response = self.fetch_url(url).json()

        if response['result'] == 'false': # bter api returns this as string
            # bter doesn't support this pair, we need to make 2 calls and
            # do the math ourselves. The extra http request isn't a problem because
            # of caching. BTER only has USD, BTC and CNY
            # markets, so any other fiat will likely fail.

            url = url_template % (crypto_symbol, 'btc')
            response = self.fetch_url(url)
            altcoin_btc = float(response['last'])

            url = url_template % ('btc', fiat_symbol)
            response = self.fetch_url(url)
            btc_fiat = float(response['last'])

            return (btc_fiat * altcoin_btc), 'bter (calculated)'

        return float(response['last'] or 0), 'bter'


class CryptonatorPriceGetter(PriceGetter):
    def get_price(self, crypto_symbol, fiat_symbol):
        pair = "%s-%s" % (crypto_symbol, fiat_symbol)
        url = "https://www.cryptonator.com/api/ticker/%s" % pair
        response = self.fetch_url(url).json()
        return float(response['ticker']['price']), 'cryptonator'


class CoinSwapPriceGetter(PriceGetter):
    def get_price(self, crypto_symbol, fiat_symbol):
        chunk = ("%s/%s" % (crypto_symbol, fiat_symbol)).upper()
        url = "https://api.coin-swap.net/market/stats/%s" % chunk
        response = self.fetch_url(url).json()
        return float(response['lastprice']), 'coin-swap'


class CryptoPriceGetter(object):
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
                # API is probably broken
                pass

        raise Exception("Can not find price for %s to %s" % (crypto_symbol, fiat_symbol))

def get_current_price(crypto_symbol, fiat_symbol, useragent=None):
    """
    High level function for getting the current price. This function will try multiple
    services until either a price is found, or if no price can be found, an exception is raised.
    """
    return CryptoPriceGetter(useragent).get_price(crypto_symbol, fiat_symbol)
