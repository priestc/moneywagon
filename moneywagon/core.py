from __future__ import print_function
import random
import requests

from concurrent import futures

useragent = 'moneywagon 1.8.3'

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
    api_homepage = '' # link to page defining the API.
    supported_cryptos = None # must be a list of lower case currency codes.
    explorer_address_url = None # url to block explerer page. Use {address} and {crypto} as placeholders.
    explorer_tx_url = None # {txid}
    explorer_blocknum_url = None # {blocknum}
    explorer_blockhash_url = None # {blockhash}

    def __init__(self, verbose=False, responses=None, timeout=None):
        self.responses = responses or {} # for caching
        self.verbose = verbose
        self.last_url = None
        self.last_raw_response = None
        self.timeout = timeout

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

        if self.timeout:
            # add timeout parameter to requests.get if one was passed in on construction...
            kwargs['timeout'] = self.timeout

        response = getattr(requests, method)(url, *args, **kwargs)

        if self.verbose:
            print("Got Response: %s" % url)

        if response.status_code == 503:
            raise SkipThisService("Service returned 503 - Temporarily out of service.")

        if method == 'get':
            self.responses[url] = response # cache for later

        self.last_raw_response = response
        return response

    def get_current_price(self, crypto, fiat, confirmations=1):
        """
        Makes call to external service, and returns the price for given
        fiat/crypto pair. Returns two item tuple: (price, best_market)
        """
        raise NotImplementedError(
            "This service does not support getting the current fiat exchange rate. "
            "Or rather it has no defined 'get_current_price' method."
        )

    def get_balance_multi(self, crypto, addresses, confirmations=1):
        """
        Same as above, except addresses are passed in as a list instead of
        just a single string.
        """
        raise NotImplementedError(
            "This service does not support getting multiple address balances. "
            "Or rather it has no defined 'get_balance_multi' method."
        )

    def get_historical_price(self, crypto, fiat, at_time):
        """
        """
        raise NotImplementedError(
            "This service does not support getting historical price. "
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

    def get_optimal_fee(self, crypto, tx_bytes):
        raise NotImplementedError(
            "This service does not support getting optimal fee. "
            "Or rather it has no defined 'get_optimal_fee' method."
        )


class AutoFallbackFetcher(object):
    """
    Calls a succession of services until one returns a value.
    """

    def __init__(self, services=None, verbose=False, responses=None, timeout=None):
        """
        Each service class is instantiated here so the service instances stay
        in scope for the entire life of this object. This way the service
        objects can cache responses.
        """
        if not services:
            from moneywagon import ALL_SERVICES
            services = ALL_SERVICES

        self.services = []
        for ServiceClass in services:
            self.services.append(
                ServiceClass(verbose=verbose, responses=responses, timeout=timeout)
            )

        self.verbose = verbose
        self._successful_service = None # gets filled in after success
        self._failed_services = []

    def _try_services(self, method_name, *args, **kwargs):
        """
        Try each service until one returns a response. This function only
        catches the bare minimum of exceptions from the service class. We want
        exceptions to be raised so the service classes can be debugged and
        fixed quickly.
        """
        for service in self.services:
            crypto = ((args and args[0]) or kwargs['crypto']).lower()
            address = kwargs.get('address', '').lower()
            fiat = kwargs.get('fiat', '').lower()

            if service.supported_cryptos and (crypto not in service.supported_cryptos):
                if self.verbose:
                    print("SKIP:", "%s not supported for %s" % (crypto, service.__class__.__name__))
                continue
            try:
                if self.verbose: print("* Trying:", service, crypto, "%s%s" % (address, fiat))
                ret =  getattr(service, method_name)(*args, **kwargs)
                self._successful_service = service
                return ret
            except (KeyError, IndexError, TypeError, ValueError, 
                    requests.exceptions.ReadTimeout, requests.exceptions.SSLError) as exc:
                # API has probably changed, therefore service class broken
                if self.verbose: print("FAIL:", service, exc.__class__.__name__, exc)
                self._failed_services.append({
                    'service': service,
                    'error': "%s %s" % (exc.__class__.__name__, exc)
                })
            except SkipThisService as exc:
                # service classes can raise this exception if for whatever reason
                # that service can't return a response, but maybe another one can.
                if self.verbose: print("SKIP:", exc.__class__.__name__, exc)
                self._failed_services.append({'service': service, 'error': "Skipped"})
            except NotImplementedError as exc:
                if self.verbose: print("SKIP:", exc.__class__.__name__, exc)
                self._failed_services.append({'service': service, 'error': "Not Implemented"})


        if not self._failed_services:
            raise NotImplementedError(
                "No Services defined for %s and %s" % (crypto, method_name)
            )

        raise NoService(self.no_service_msg(*args, **kwargs))

    def no_service_msg(self, *args, **kwargs):
        """
        This function is called when all Services have been tried and no value
        can be returned. It much take the same args and kwargs as in the method
        spefified in `method_name`. Returned is a string for the error message.
        It should say something informative.
        """
        return "All either skipped or failed."


def enforce_service_mode(services, FetcherClass, kwargs, modes):
    """
    Fetches the value according to the mode of execution desired.
    `FetcherClass` must be a class that is subclassed from AutoFallbackFetcher.
    `services` must be a list of Service classes.
    `kwargs` is a list of arguments used to make the service call, usually
      something like {crypto: 'btc', address: '1HwY...'} or
      {crypto: 'ltc', fiat: 'rur'}, (depends on the what FetcherClass.action takes)

    Modes can be:

         average = positive int. 1 by default. Takes average of n fetches.
         verbose = [True|False] False by default. Extra output.
         random = [True|False] False by default. Randomizes service order.
         paranoid = positive int. 1 by default. Redundant Fetching.
         fast = positive int. 0 by default. Return as soon as recieved first n results.

    """
    fast_level = modes.get('fast', 0)
    average_level = modes.get('average', 0)
    paranoid_level = modes.get('paranoid', 0)
    verbose = modes.get('verbose', False)
    timeout = modes.get('timeout', None)

    if modes.get('random', False):
        random.shuffle(services)

    if average_level <= 1 and paranoid_level <= 1 and fast_level == 0:
        # only need to make 1 external call, no need for threading...
        return FetcherClass(services=services, verbose=verbose, timeout=timeout).action(**kwargs)

    elif average_level > 1:
        # instead of checking that all results are the same, we just return the average of all results.
        # mostly useful for non-blockchain operations like price and optimal fee.
        results = _get_results(FetcherClass, services, num_results=average_level, verbose=verbose, timeout=timeout)
        if hasattr(FetcherClass, "simplify_for_average"):
            simplified = [FetcherClass.simplify_for_average(x) for x in results]
        else:
            simplified = results
        return sum(simplified) / len(simplified)

    elif paranoid_level > 1:
        results = _get_results(
            FetcherClass, services, kwargs, num_results=paranoid_level, verbose=verbose, timeout=timeout
        )

    elif fast_level >= 1:
        raise Exception("Fast mode not yet working")
        results = _get_results(
            FetcherClass, services, kwargs, fast=fast_level, verbose=verbose
        )

    else:
        raise Exception("No mode specified.")


    if hasattr(FetcherClass, "strip_for_consensus"):
        to_compare = FetcherClass.strip_for_consensus(results)
    else:
        to_compare = results

    if len(set(to_compare)) == 1:
        # if all values match, return any one (in this case the first one).
        return results[0]
    else:
        raise ServiceDisagreement("Differing values returned: %s" % results)


def _get_results(FetcherClass, services, kwargs, num_results=None, fast=0, verbose=False, timeout=None):
    """
    Does the fetching in multiple threads of needed. Used by paranoid and fast mode.
    """
    if not num_results or fast:
        num_results = len(services)

    with futures.ThreadPoolExecutor(max_workers=len(services)) as executor:
        fetches = [
            executor.submit(
                FetcherClass(services=[service], verbose=verbose, timeout=timeout).action, **kwargs
            ) for service in services[:num_results]
        ]

        results = []

        if fast == 1:
            # ths code is a work in progress. futures.FIRST_COMPLETED works differently than I thought...
            to_iterate, still_going = futures.wait(fetches, return_when=futures.FIRST_COMPLETED)
            for x in still_going:
                try:
                    x.result(timeout=1.001)
                except futures._base.TimeoutError:
                    pass

        elif fast > 1:
            raise Exception("fast level greater than 1 not yet implemented")
        else:
            to_iterate = futures.as_completed(fetches)

        for future in to_iterate:
            results.append(future.result())

    return results

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

def get_optimal_services(crypto, type_of_service):
    from .crypto_data import crypto_data
    try:
        # get best services from curated list
        return crypto_data[crypto.lower()]['services'][type_of_service]
    except KeyError:
        raise ValueError("Invalid cryptocurrency symbol: %s" % crypto)

def get_magic_bytes(crypto):
    from .crypto_data import crypto_data
    try:
        pub_byte = crypto_data[crypto]['address_version_byte']
        priv_byte = crypto_data[crypto]['private_key_prefix']
        if priv_byte >= 128:
            priv_byte -= 128 #pybitcointools bug
        return pub_byte, priv_byte

    except KeyError:
        raise ValueError("Invalid cryptocurrency symbol: %s" % crypto)
