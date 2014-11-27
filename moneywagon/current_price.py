import requests

class SkipThisGetter(Exception):
    pass

class PriceGetter(object):
    """
    All getters should subclass this class, and implement their own `get_price` function
    """

    def __init__(self, useragent=None, verbose=False, responses=None):
        self.useragent = useragent or 'pycryptoprices 1.0'
        self.responses = responses or {} # for caching
        self.verbose = verbose

    def __repr__(self):
        return "%s (%s in cache)" % (self.__class__.__name__, len(self.responses))

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

        if self.verbose: print("request: %s" % url)

        response = requests.get(*args, **kwargs)
        self.responses[url] = response # cache for later
        return response

    def get_price(self, crypto, fiat):
        """
        Makes call to external service, and returns the price for given
        fiat/crypto pair. Returns two item tuple: (price, best_market)
        """
        raise NotImplementedError()


class OldCryptoCoinChartsPriceGetter(PriceGetter):
    """
    Using raw rest API (looks to be currently broken)
    """
    def get_price(self, crypto, fiat):
        url = "http://api.cryptocoincharts.info/tradingPairs/%s_%s" % (
            crypto, fiat
        )
        response = self.fetch_url(url).json()
        return float(response['price'] or 0), response['best_market']


class CryptoCoinChartsPriceGetter(PriceGetter):
    """
    Using fancy API client library (currently broken)
    """
    def get_price(self, crypto, fiat):
        from CryptoCoinChartsApi import API as CCCAPI
        api = CCCAPI()
        tradingpair = api.tradingpair("%s_%s" % (crypto, fiat))
        return tradingpair.price, tradingpair.best_market


class BTERPriceGetter(PriceGetter):
    def get_price(self, crypto, fiat):
        url_template = "http://data.bter.com/api/1/ticker/%s_%s"
        url = url_template % (crypto, fiat)

        response = self.fetch_url(url).json()

        if response['result'] == 'false': # bter api returns this as string
            # bter doesn't support this pair, we need to make 2 calls and
            # do the math ourselves. The extra http request isn't a problem because
            # of caching. BTER only has USD, BTC and CNY
            # markets, so any other fiat will likely fail.

            url = url_template % (crypto, 'btc')
            response = self.fetch_url(url)
            altcoin_btc = float(response['last'])

            url = url_template % ('btc', fiat)
            response = self.fetch_url(url)
            btc_fiat = float(response['last'])

            return (btc_fiat * altcoin_btc), 'bter (calculated)'

        return float(response['last'] or 0), 'bter'


class CryptonatorPriceGetter(PriceGetter):
    def get_price(self, crypto, fiat):
        pair = "%s-%s" % (crypto, fiat)
        url = "https://www.cryptonator.com/api/ticker/%s" % pair
        response = self.fetch_url(url).json()
        return float(response['ticker']['price']), 'cryptonator'


class CoinSwapPriceGetter(PriceGetter):
    def get_price(self, crypto, fiat):
        chunk = ("%s/%s" % (crypto, fiat)).upper()
        url = "https://api.coin-swap.net/market/stats/%s" % chunk
        response = self.fetch_url(url).json()
        return float(response['lastprice']), 'coin-swap'


class BitstampPriceGetter(PriceGetter):
    def get_price(self, crypto, fiat):
        if fiat.lower() != 'usd' or crypto.lower() != 'btc':
            raise SkipThisGetter('Bitstamp only does USD->BTC')

        url = "https://www.bitstamp.net/api/ticker/"
        response = self.fetch_url(url).json()
        return (float(response['last']), 'bitstamp')


class BTCEPriceGetter(PriceGetter):
    def get_price(self, crypto, fiat):
        pair = "%s_%s" % (crypto, fiat)
        url = "https://btc-e.com/api/3/ticker/" + pair
        response = self.fetch_url(url).json()
        return (response[pair]['last'], 'btc-e')
