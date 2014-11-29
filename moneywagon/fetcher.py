from __future__ import print_function
import requests

useragent = 'moneywagon 1.0.1'

class SkipThisFetcher(Exception):
    pass

class Fetcher(object):
    """
    All fetchers should subclass this class, and implement their own `get_price` function
    """
    supported_cryptos = None

    def __init__(self, useragent=None, verbose=False, responses=None):
        self.responses = responses or {} # for caching
        self.verbose = verbose

    def __repr__(self):
        return "%s (%s in cache)" % (self.__class__.__name__, len(self.responses))

    def get_url(self, url, *args, **kwargs):
        return self._external_request('get', url, *args, **kwargs)

    def post_url(self, url, *args, **kwargs):
        return self._external_request('post', url, *args, **kwargs)

    def _external_request(self, method, url, *args, **kwargs):
        """
        Wrapper for requests.get with useragent automatically set.
        And also all requests are reponses are cached.
        """
        if url in self.responses.keys() and method == 'get':
            return self.responses[url] # return from cache if its there

        headers = kwargs.pop('headers', None)
        custom = {'User-Agent': useragent}
        if headers:
            headers.update(custom)
            kwargs['headers'] = headers
        else:
            kwargs['headers'] = custom

        if self.verbose: print("URL: %s" % url)

        response = getattr(requests, method)(url, *args, **kwargs)
        if method == 'get':
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

    def get_transactions(self, crypto, address):
        raise NotImplementedError()

    def get_balance(self, crypto, address):
        raise NotImplementedError()


class AutoFallback(object):
    """
    Calls a succession of getters until one returns a value.
    """
    getter_classes = [] # must be class instances of getter
    method_name = None # the relevant name of the method on each getter class

    def __init__(self, verbose=False, responses=None):
        self.getters = []
        for Getter in self.getter_classes:
            self.getters.append(
                Getter(verbose=verbose, responses=responses)
            )

        self.verbose = verbose

    def _try_each_getter(self, *args, **kwargs):
        for getter in self.getters:
            crypto = (args and args[0]) or kwargs['crypto']
            if getter.supported_cryptos and (crypto.lower() not in getter.supported_cryptos):
                if self.verbose:
                    print("SKIP:", "%s not supported for %s" % (crypto, getter.__class__.__name__))
                continue
            try:
                if self.verbose: print("* Trying:", getter)
                return getattr(getter, self.method_name)(*args, **kwargs)
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                # API has probably changed, therefore getter class broken
                if self.verbose: print("FAIL:", exc.__class__.__name__, exc)
            except SkipThisFetcher as exc:
                # getter classes can raise this exception if for whatever reason
                # that getter can't return a response, but maybe another one can.
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
