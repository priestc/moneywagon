from __future__ import print_function
import requests

useragent = 'moneywagon 1.0.1'

class SkipThisService(Exception):
    pass

class NoService(Exception):
    pass

class NoData(Exception):
    pass

class Service(object):
    """
    All Services should subclass this class, and implement their own `get_price` function
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
    Calls a succession of services until one returns a value.
    """
    service_classes = [] # must be class instances of service
    method_name = None # the relevant name of the method on each service class

    def __init__(self, verbose=False, responses=None):
        self.services = []
        for service in self.service_classes:
            self.services.append(
                service(verbose=verbose, responses=responses)
            )

        self.verbose = verbose

    def _try_each_service(self, *args, **kwargs):
        for service in self.services:
            crypto = (args and args[0]) or kwargs['crypto']
            if service.supported_cryptos and (crypto.lower() not in service.supported_cryptos):
                if self.verbose:
                    print("SKIP:", "%s not supported for %s" % (crypto, service.__class__.__name__))
                continue
            try:
                if self.verbose: print("* Trying:", service)
                return getattr(service, self.method_name)(*args, **kwargs)
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                # API has probably changed, therefore service class broken
                if self.verbose: print("FAIL:", exc.__class__.__name__, exc)
            except SkipThisService as exc:
                # service classes can raise this exception if for whatever reason
                # that service can't return a response, but maybe another one can.
                if self.verbose: print("SKIP:", exc)

        raise NoService(self.no_service_msg(*args, **kwargs))

    def no_service_msg(self, *args, **kwargs):
        """
        This function is called when all Services have been tried and no value
        can be returned. It much take the same args and kwargs as in the method
        spefified in `self.method_name`. Returned is a string for the error message.
        It should say something informative.
        """
        return "All either skipped or failed."
