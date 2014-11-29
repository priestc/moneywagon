from __future__ import print_function
import requests

class SkipThisFetcher(Exception):
    pass

class Fetcher(object):
    """
    All getters should subclass this class, and implement their own `get_price` function
    """

    def __init__(self, useragent=None, verbose=False, responses=None):
        self.useragent = useragent or 'moneywagon 1.0.1'
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

    def get_historical(self, crypto, fiat, at_time):
        raise NotImplementedError()
