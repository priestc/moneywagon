from __future__ import print_function
import random
import requests

from concurrent import futures

useragent = 'moneywagon 1.3.0'

class ServiceDisagreement(Exception):
    pass

class NoService(Exception):
    pass

class SkipThisService(NoService):
    pass

class NoData(Exception):
    pass

class Service(object):
    """
    Represents a blockchain service running an Http interface.
    Some `Services` subclass will only support a subset of all pissible blockchain functions.
    All Services should subclass this class, and implement their own `get_*` method.
    """
    supported_cryptos = None # must be a list of lower case currency codes.

    def __init__(self, verbose=False, responses=None):
        self.responses = responses or {} # for caching
        self.verbose = verbose
        self.last_url = None
        self.last_raw_response = None

    def __repr__(self):
        return "<Service: %s (%s in cache)>" % (self.__class__.__name__, len(self.responses))

    def get_url(self, url, *args, **kwargs):
        return self._external_request('get', url, *args, **kwargs)

    def post_url(self, url, *args, **kwargs):
        return self._external_request('post', url, *args, **kwargs)

    def _external_request(self, method, url, *args, **kwargs):
        """
        Wrapper for requests.get with useragent automatically set.
        And also all requests are reponses are cached.
        """
        self.last_url = url
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

        self.last_raw_response = response
        return response

    def get_current_price(self, crypto, fiat):
        """
        Makes call to external service, and returns the price for given
        fiat/crypto pair. Returns two item tuple: (price, best_market)
        """
        raise NotImplementedError(
            "This service does not support getting the current fiat exchange rate."
            "Or rather it has no defined 'get_current_price' method."
        )

    def get_historical_price(self, crypto, fiat, at_time):
        """
        """
        raise NotImplementedError(
            "This service does not support getting historical price."
            "Or rather it has no defined 'get_historical_price' method."
        )

    def get_transactions(self, crypto, address, confirmations=1):
        """
        Must be returned with the most recent transaction at the top.
        Returned is a list of dicts that have the following keys:

        `amount`: Number of units of currency moved. Always in base units (not satoshis).
        `date`: a datetime object of when the transaction was made.
        `txid`: The transaction ID, looks like a hash.
        `confirmations`: integer of the number of confirmations this transaction has on top of it.

        """
        raise NotImplementedError(
            "This service does not support getting historical transactions. "
            "Or rather it has no defined 'get_transactions' method."
        )

    def get_unspent_outputs(self, crypto, address):
        """
        Default implmentation of this function that uses get_transaction
        Subclasses should overwrite this with a direct call to get utxo (if applicable)

        Returned will be a list of dictionaries, the keys will be:

        required:

        `output` - the big endian tx hash, followed by a colon, then the tx index. (for pybitcointools support)
        `address` - the address passed in (for pybitcointools support)
        `amount` - int, satoshi amount of the input

        optional:

        `confirmations` - how many confirmations this tx has so far.

        """
        raise NotImplementedError(
            "This service does not support getting unspent outputs. "
            "Or rather it has no defined 'get_unspent_outputs' method."
        )

    def get_balance(self, crypto, address, confirmations=1):
        """
        Get the amount of coin in the address passed in.
        Always returns a single float.
        """
        raise NotImplementedError(
            "This service does not support getting address balances. "
            "Or rather it has no defined 'get_balance' method."
        )

    def push_tx(self, crypto, tx_hex):
        """
        Push transaction to the miner network. Returns txid if done
        successfully.
        """
        raise NotImplementedError(
            "This service does not support pushing transactions to the network. "
            "Or rather it has no defined 'push_tx' method."
        )

    def get_block(self, crypto, block_height='', block_number='', latest=False):
        """
        Get block based on either block height, block number or get the latest
        block. Only one of the previous arguments must be passed on.

        Returned is a dictionary object with the following keys:

        * required fields:

        block_number - int
        size - size of block
        time - datetime object of when the block was made
        hash - str (must be all lowercase)
        tx_count - int, the number of transactions included in thi block.

        * optional fields:

        confirmations - int
        sent_value - total value moved from all included transactions
        total_fees - total amount of tx fees from all included transactions
        mining_difficulty - what the difficulty was when this block was made.
        merkle_root - str (lower case)
        previous_hash - str (lower case)
        next_hash - str (lower case) (or `None` of its the latest block)
        """
        raise NotImplementedError(
            "This service does not support getting getting block data. "
            "Or rather it has no defined 'get_block' method."
        )

    def get_optimal_fee(self, crypto, tx_bytes, acceptable_block_delay):
        raise NotImplementedError(
            "This service does not support getting optimal fee. "
            "Or rather it has no defined 'get_optimal_fee' method."
        )


class AutoFallback(object):
    """
    Calls a succession of services until one returns a value.
    """
    service_method_name = None # the relevant name of the method on each service class

    def __init__(self, services=None, verbose=False, responses=None):
        """
        Each service class is instantiated here so the service instances stay
        in scope for the entire life of this object. This way the service
        objects can cache responses.
        """
        if not services:
            from moneywagon.services import ALL_SERVICES
            services = ALL_SERVICES

        self.services = []
        for ServiceClass in services:
            self.services.append(
                ServiceClass(verbose=verbose, responses=responses)
            )

        self.verbose = verbose

    def _try_each_service(self, *args, **kwargs):
        """
        Try each service until one returns a response. This function only
        catches the bare minimum of exceptions from the service class. We want
        exceptions to be raised so the service classes can be debugged and
        fixed quickly.
        """
        for service in self.services:
            crypto = ((args and args[0]) or kwargs['crypto']).lower()
            if service.supported_cryptos and (crypto not in service.supported_cryptos):
                if self.verbose:
                    print("SKIP:", "%s not supported for %s" % (crypto, service.__class__.__name__))
                continue
            try:
                if self.verbose: print("* Trying:", service)
                return getattr(service, self.service_method_name)(*args, **kwargs)
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                # API has probably changed, therefore service class broken
                if self.verbose: print("FAIL:", exc.__class__.__name__, exc)
            except SkipThisService as exc:
                # service classes can raise this exception if for whatever reason
                # that service can't return a response, but maybe another one can.
                if self.verbose: print("SKIP:", exc.__class__.__name__, exc)
            except NotImplementedError as exc:
                if self.verbose: print("SKIP:", exc.__class__.__name__, exc)

        raise NoService(self.no_service_msg(*args, **kwargs))

    def no_service_msg(self, *args, **kwargs):
        """
        This function is called when all Services have been tried and no value
        can be returned. It much take the same args and kwargs as in the method
        spefified in `self.method_name`. Returned is a string for the error message.
        It should say something informative.
        """
        return "All either skipped or failed."

def enforce_service_mode(services, modes, FetcherClass, kwargs, verbose=False):
    """
    Fetches the value according to the mode of execution desired.
    `FetcherClass` must be a class that is subclassed from AutoFallback.
    `services` must be a list of Service classes.
    `kwargs` is a list of arguments used to make the service call, usually
      something like {crypto: 'btc', address: '1HwY...'} or
      {crypto: 'ltc', fiat: 'rur'}, (depends on the what FetcherClass.get takes)
    """
    paranoid_level = modes['paranoid']

    if modes['random']:
        random.shuffle(services)

    if paranoid_level == 1:
        return FetcherClass(services=services, verbose=verbose).get(**kwargs)

    with futures.ThreadPoolExecutor(max_workers=len(services)) as executor:
        fetches = [
            executor.submit(
                FetcherClass(services=[service], verbose=verbose).get, **kwargs
            ) for service in services
        ]

        results = []
        for future in futures.as_completed(fetches):
            results.append(future.result())

    if hasattr(FetcherClass, "strip_for_consensus"):
        to_compare = FetcherClass.strip_for_consensus(results)
    else:
        to_compare = results

    if len(set(to_compare)) == 1:
        # if all values match, return any one (in this case the first one).
        return results[0]
    else:
        raise ServiceDisagreement("Differing values returned: %s" % results)

def currency_to_protocol(amount):
    """
    Convert a string of 'currency units' to 'protocol units'. For instance
    converts 19.1 bitcoin to 1910000000 satoshis.

    Input is a float, output is an integer that is 1e8 times larger.

    It is hard to do this conversion because multiplying
    floats causes rounding nubers which will mess up the transactions creation
    process.

    examples:

    19.1 -> 1910000000
    0.001 -> 100000

    """
    if type(amount) == float:
        amount = "%.8f" % amount

    return int(amount.replace(".", '')) # avoiding float math
