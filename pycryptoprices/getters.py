import requests

class PriceGetter(object):
    """
    All getters should subclass this class, and implement their own `get_price` function
    """

    def __init__(self, useragent='pycryptoprices 1.0'):
        self.useragent = useragent
        self.responses = {}

    def fetch_url(*args, **kwargs):
        """
        Wrapper for requests.get with useragent automatically set.
        """
        url = args[0]
        if self.responses[url]:
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
        raise NotImplementedError()


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

        response = fetch_url(url).json()

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
        response = fetch_url(url).json()
        return float(response['ticker']['price']), 'cryptonator'


class CoinSwapPriceGetter(PriceGetter):
    def get_price(self, crypto_symbol, fiat_symbol):
        chunk = ("%s/%s" % (crypto_symbol, fiat_symbol)).upper()
        url = "https://api.coin-swap.net/market/stats/%s" % chunk
        response = fetch_url(url).json()
        return float(response['lastprice']), 'coin-swap'
