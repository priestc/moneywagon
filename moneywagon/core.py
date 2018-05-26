from __future__ import print_function
import random
import json
from subprocess import check_output, CalledProcessError, STDOUT
import requests
import time
import datetime
import os
import pkg_resources

from bitcoin import serialize
from concurrent import futures

__version__ = pkg_resources.get_distribution('moneywagon').version
useragent = "Moneywagon %s" % __version__

class ServiceDisagreement(Exception):
    pass

class NoService(Exception):
    pass

class SkipThisService(NoService):
    pass

class ServiceError(NoService):
    pass

class CurrencyNotSupported(Exception):
    pass

class NoServicesDefined(Exception):
    pass

class NoData(Exception):
    pass

class RevertToPrivateMode(NotImplementedError):
    pass

class ClassProperty(property):
    """
    From http://stackoverflow.com/a/1383402/118495
    """
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class Service(object):
    """
    Represents a blockchain service running an Http interface.
    Some `Services` subclass will only support a subset of all pissible blockchain functions.
    All Services should subclass this class, and implement their own `get_*` method.
    """
    domain = None # optional, useful if the service will have subclasses
    api_homepage = '' # link to page defining the API.
    protocol = 'https'
    supported_cryptos = None # must be a list of lower case currency codes.
    explorer_address_url = None # url to block explerer page. Use {address} and {crypto} as placeholders.
    explorer_tx_url = None # {txid}
    explorer_blocknum_url = None # {blocknum}
    explorer_blockhash_url = None # {blockhash}
    ssl_verify = True
    socketio_url = None
    exchange_fee_rate = None
    api_key = False
    symbol_mapping = None

    @ClassProperty
    @classmethod
    def name(cls):
        return cls.__name__

    def __init__(self, verbose=False, responses=None, timeout=None, random_wait_seconds=0, api_key=None, api_secret=None):
        self.responses = responses or {} # for caching
        self.verbose = verbose
        self.last_url = None
        self.last_raw_response = None
        self.timeout = timeout
        self.random_wait_seconds = random_wait_seconds
        self.api_key = api_key
        self.api_secret = api_secret
        self.total_external_fetch_duration = datetime.timedelta(0)

        try:
            with open(os.path.expanduser('~/.exchange_keys')) as f:
                config = json.loads(f.read())

            for key, value in config[self.name].items():
                if not hasattr(self, key) or not getattr(self, key):
                    # only load if no other values have been passed in.
                    setattr(self, key, str(value))
        except KeyError:
            pass # no key found
        except Exception as exc:
            if verbose:
                print("config file broke", str(exc))


    def __repr__(self):
        return "<Service: %s (%s in cache)>" % (self.__class__.__name__, len(self.responses))

    def get_url(self, url, *args, **kwargs):
        return self._external_request('get', url, *args, **kwargs)

    def post_url(self, url, *args, **kwargs):
        return self._external_request('post', url, *args, **kwargs)

    def delete_url(self, url, *args, **kwargs):
        return self._external_request('delete', url, *args, **kwargs)

    def check_error(self, response):
        """
        If the service is returning an error, this function should raise an exception.
        such as SkipThisService
        """
        if response.status_code == 500:
            raise ServiceError("500 - " + response.content)

        if response.status_code == 503:
            if "DDoS protection by Cloudflare" in response.content:
                raise ServiceError("Foiled by Cloudfare's DDoS protection")
            raise ServiceError("503 - Temporarily out of service.")

        if response.status_code == 429:
            raise ServiceError("429 - Too many requests")

        if response.status_code == 404:
            raise ServiceError("404 - Not Found")

        if response.status_code == 400:
            raise ServiceError("400 - Bad Request")

    def convert_currency(self, base_fiat, base_amount, target_fiat):
        """
        Convert one fiat amount to another fiat. Uses the fixer.io service.
        """
        url = "http://api.fixer.io/latest?base=%s" % base_fiat
        data = self.get_url(url).json()
        try:
            return data['rates'][target_fiat.upper()] * base_amount
        except KeyError:
            raise Exception("Can not convert %s to %s" % (base_fiat, target_fiat))

    def make_market(self, crypto, fiat):
        """
        Make market identifier the service can understand with the passed in
        moneywagon format crypto and fiat. Usually calls `self.fix_symbol`.
        """
        raise NotImplementedError()

    def fix_symbol(self, symbol, reverse=False):
        """
        In comes a moneywagon format symbol, and returned in the symbol converted
        to one the service can understand.
        """
        if not self.symbol_mapping:
            return symbol

        for old, new in self.symbol_mapping:
            if reverse:
                if symbol == new:
                    return old
            else:
                if symbol == old:
                    return new

        return symbol

    def parse_market(self, market, split_char='_'):
        """
        In comes the market identifier directly from the service. Returned is
        the crypto and fiat identifier in moneywagon format.
        """
        crypto, fiat = market.lower().split(split_char)
        return (
            self.fix_symbol(crypto, reverse=True),
            self.fix_symbol(fiat, reverse=True)
        )

    def make_market(self, crypto, fiat, seperator="_"):
        """
        Convert a crypto and fiat to a "market" string. All exchanges use their
        own format for specifying markets. Subclasses can define their own
        implementation.
        """
        return ("%s%s%s" % (
            self.fix_symbol(crypto), seperator, self.fix_symbol(fiat))
        ).lower()

    def make_rpc_call(self, args, internal=False, skip_json=False):
        cmd = [self.cli_path] + [str(a) for a in args]
        if not self.cli_path:
            raise SkipThisService("No CLI path defined")
        try:
            raw = check_output(cmd, stderr=STDOUT)
        except CalledProcessError as exc:
            raise SkipThisService("Full node CLI call failed: %s" % exc.output)
        except OSError as exc:
            raise SkipThisService(str(exc))

        if not internal:
            self.last_raw_response = raw
            self.last_url = " ".join(cmd)

        ret = raw
        if not skip_json:
            ret = json.loads(raw)

        return ret

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

        start = datetime.datetime.now()
        response = getattr(requests, method)(url, verify=self.ssl_verify, *args, **kwargs)
        self.total_external_fetch_duration += datetime.datetime.now() - start

        if self.verbose:
            print("Got Response: %s (took %s)" % (url, (datetime.datetime.now() - start)))

        self.last_raw_response = response

        self.check_error(response)

        if method == 'get':
            self.responses[url] = response # cache for later

        return response

    def get_current_price(self, crypto, fiat):
        """
        Makes call to external service, and returns the price for given
        fiat/crypto pair. Returned is a float.
        """
        raise NotImplementedError(
            self.name + " does not support getting the current fiat exchange rate. "
            "Or rather it has no defined 'get_current_price' method."
        )

    def get_historical_price(self, crypto, fiat, at_time):
        """
        """
        raise NotImplementedError(
            self.name + " does not support getting historical price. "
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
            self.name + " does not support getting historical transactions. "
            "Or rather it has no defined 'get_transactions' method."
        )

    def get_transactions_multi(self, crypto, addresses, confirmations=1):
        raise NotImplementedError(
            self.name + " does not support getting historical transactions by multiple addresses. "
            "Or rather it has no defined 'get_transactions_multi' method."
        )

    def get_single_transaction(self, crypto, txid):
        """
        Get detailed information about a single transaction.

        time - datetime, when this transaction was confirmed.
        block_hash - string, the id of the block this tx is confirmed in.
        block_number - integer, which block number this tx is confirmed in.
        hex - the entire tx encoded in hex format
        size - size of TX in bytes.
        inputs - list of {address:, amount:, txid:}, amount is in satoshis
        outputs - list of {address:, amount:, scriptPubKey:}, amount is in satoshis, scriptPubKey is hex
        txid
        total_out - (in satoshis)
        total_ins - (in satoshis)
        confirmations - number of confirmations this TX curently has
        fee - total amount of fees this TX leaves for miners (in satoshis)

        """
        raise NotImplementedError(
            self.name + " does not support getting single transactions. "
            "Or rather it has no defined 'get_single_transaction' method."
        )

    def get_single_transaction_multi(self, crypto, txids):
        raise NotImplementedError(
            self.name + " does not support getting single transactions by multiple txids. "
            "Or rather it has no defined 'get_single_transaction_multi' method."
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
        `scriptPubKey` - string
        `txid` - string
        `vout` - integer

        optional:

        `confirmations` - how many confirmations this tx has so far.
        `scriptPubKey_asm` - string

        """
        raise NotImplementedError(
            self.name + " does not support getting unspent outputs. "
            "Or rather it has no defined 'get_unspent_outputs' method."
        )

    def get_unspent_outputs_multi(self, crypto, addresses):
        raise NotImplementedError(
            self.name + " does not support getting unspent outputs by multiple addresses. "
            "Or rather it has no defined 'get_unspent_outputs_multi' method."
        )

    def get_balance(self, crypto, address, confirmations=1):
        """
        Get the amount of coin in the address passed in.
        Always returns a single float.
        """
        raise NotImplementedError(
            self.name + " does not support getting address balances. "
            "Or rather it has no defined 'get_balance' method."
        )

    def get_balance_multi(self, crypto, addresses, confirmations=1):
        """
        Same as above, except addresses are passed in as a list instead of
        just a single string.
        """
        raise NotImplementedError(
            self.name + " does not support getting multiple address balances. "
            "Or rather it has no defined 'get_balance_multi' method."
        )

    def push_tx(self, crypto, tx_hex):
        """
        Push transaction to the miner network. Returns txid if done
        successfully.
        """
        raise NotImplementedError(
            self.name + " does not support pushing transactions to the network. "
            "Or rather it has no defined 'push_tx' method."
        )

    def get_block(self, crypto, block_hash='', block_number='', latest=False):
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
        miner - name of miner that first relayed this block
        version - block version
        """
        raise NotImplementedError(
            self.name + " does not support getting getting block data. "
            "Or rather it has no defined 'get_block' method."
        )

    def get_optimal_fee(self, crypto, tx_bytes):
        raise NotImplementedError(
            self.name + " does not support getting optimal fee. "
            "Or rather it has no defined 'get_optimal_fee' method."
        )

    def get_pairs(self):
        """
        Only for exchanges. Returns list of all trading pairs supported by this
        service. All items are lower case, and seperated with a "-".
        """
        raise NotImplementedError(
            self.name + " does not support getting all exchange pairs. "
            "Or rather it has no defined 'get_pairs' method."
        )

    def get_orderbook(self, crypto, fiat):
        """
        Only for exchznges. Returns the current orderbook as a dict with two keys:
        bids and asks. Each is a list of floats. The first float is price, the
        second is order size.
        """
        raise NotImplementedError(
            self.name + " does not support getting orderbook. "
            "Or rather it has no defined 'get_orderbook' method."
        )

    def make_order(self, crypto, fiat, amount, price, type="limit"):
        """
        This method buys or sells `crypto` on an exchange using `fiat` balance.
        Type can either be "fill-or-kill", "post-only", "market", or "limit".
        To get what modes are supported, consult make_order.supported_types
        if one is defined.
        """
        raise NotImplementedError(
            self.name + " does not support making orders. "
            "Or rather it has no defined 'make_order' method."
        )

    def cancel_order(self, order_id):
        raise NotImplementedError(
            self.name + " does not support canceling orders. "
            "Or rather it has no defined 'cancel_order' method."
        )

    def list_orders(self, status="open"):
        raise NotImplementedError(
            self.name + " does not support listing orders. "
            "Or rather it has no defined 'list_orders' method."
        )

    def initiate_withdraw(self, crypto, amount, address):
         raise NotImplementedError(
             self.name + " does not support initiating withdraws. "
             "Or rather it has no defined 'initiate_withdraw' method."
         )

    def get_deposit_address(self, crypto):
        raise NotImplementedError(
            self.name + " does not support getting deposit addresses. "
            "Or rather it has no defined 'get_deposit_address' method."
        )

    def get_exchange_balance(self, crypto, type="available"):
        """
        Gives you the balance you have on that exchange. Not to be confused with
        `get_balance`, which is for address balance. Returned is a float.
        """
        raise NotImplementedError(
            self.name + " does not support getting exchange balance. "
            "Or rather it has no defined 'get_exchange_balance' method."
        )

    def get_total_exchange_balances(self):
        """
        Returns balances for all currencies held on this service. Returned is a
        dictionary with currency code as key and float as the value.
        """
        raise NotImplementedError(
            self.name + " does not support getting total exchange balances. "
            "Or rather it has no defined 'get_total_exchange_balances' method."
        )

    def generate_new_deposit_address(self, crypto):
        raise NotImplementedError(
            self.name + " does not support generating new deposit address. "
            "Or rather it has no defined 'generate_new_deposit_address' method."
        )

class AutoFallbackFetcher(object):
    """
    Calls a succession of services until one returns a value.
    """

    def __init__(self, services=None, verbose=False, responses=None, timeout=None, random_wait_seconds=0):
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
        self.random_wait_seconds = random_wait_seconds

    def _try_services(self, method_name, *args, **kwargs):
        """
        Try each service until one returns a response. This function only
        catches the bare minimum of exceptions from the service class. We want
        exceptions to be raised so the service classes can be debugged and
        fixed quickly.
        """
        crypto = ((args and args[0]) or kwargs['crypto']).lower()
        address = kwargs.get('address', '').lower()
        fiat = kwargs.get('fiat', '').lower()

        if not self.services:
            raise CurrencyNotSupported("No services defined for %s for %s" % (method_name, crypto))

        if self.random_wait_seconds > 0:
            # for privacy... To avoid correlating addresses to same origin
            # only gets called before the first service call. Does not pause
            # before each and every call.
            pause_time = random.random() * self.random_wait_seconds
            if self.verbose:
                print("Pausing for: %.2f seconds" % pause_time)
            time.sleep(pause_time)

        for service in self.services:
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
                    requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
                # API has probably changed, therefore service class broken
                if self.verbose: print("FAIL:", service, exc.__class__.__name__, exc)
                self._failed_services.append({
                    'service': service,
                    'error': "%s %s" % (exc.__class__.__name__, exc)
                })
            except NoService as exc:
                # service classes can raise this exception if for whatever reason
                # that service can't return a response, but maybe another one can.
                if self.verbose: print("SKIP:", exc.__class__.__name__, exc)
                self._failed_services.append({'service': service, 'error': "Skipped: %s" % str(exc)})
            except NotImplementedError as exc:
                if self.verbose: print("SKIP:", exc.__class__.__name__, exc)
                self._failed_services.append({'service': service, 'error': "Not Implemented"})


        if not self._failed_services:
            raise NotImplementedError(
                "No Services defined for %s and %s" % (crypto, method_name)
            )

        if set(x['error'] for x in self._failed_services) == set(['Not Implemented']) and method_name.endswith("multi"):
            # some currencies may not have any multi functions defined, so retry
            # with private mode (which tries multiple services).
            raise RevertToPrivateMode("All services do not implement %s service" % method_name)

        failed_msg = ', '.join(
            ["{service.name} -> {error}".format(**x) for x in self._failed_services]
        )
        raise NoService(self.no_service_msg(*args, **kwargs) + "! Tried: " + failed_msg)

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
    private_level = modes.get('private', 0)
    verbose = modes.get('verbose', False)
    timeout = modes.get('timeout', None)

    if len(services) == 0:
        raise NoService("No services defined")

    if modes.get('random', False):
        random.shuffle(services)

    if private_level  > 0:
        results = _do_private_mode(
            FetcherClass, services, kwargs, random_wait_seconds=private_level,
            verbose=verbose, timeout=timeout
        )
        return results

    elif average_level <= 1 and paranoid_level <= 1 and fast_level == 0:
        # only need to make 1 external call, no need for threading...
        fetcher = FetcherClass(services=services, verbose=verbose, timeout=timeout)
        consensus_results = fetcher.action(**kwargs)
        used_services = [fetcher._successful_service]

    elif average_level > 1:
        # instead of checking that all results are the same, we just return the average of all results.
        # mostly useful for non-blockchain operations like price and optimal fee.
        results = _get_results(
            FetcherClass, services, kwargs, num_results=average_level, verbose=verbose, timeout=timeout
        )

        to_compare, used_services = _prepare_consensus(FetcherClass, results)
        consensus_results = sum(to_compare) / len(to_compare)

    elif paranoid_level > 1:
        results = _get_results(
            FetcherClass, services, kwargs, num_results=paranoid_level, verbose=verbose, timeout=timeout
        )
        to_compare, used_services = _prepare_consensus(FetcherClass, results)

        if len(set(to_compare)) > 1:
            full_results = zip(used_services, to_compare)
            show_error = ", ".join("%s: %s" % (s.name, v) for s, v in full_results)
            sd = ServiceDisagreement("No service consensus: %s" % show_error)
            sd.network_results = {
                service: result for service, result in full_results
            }
            raise sd

        # if all values match, return any one (in this case the first one).
        # also return the list of all services that confirm this result.
        consensus_results = results[0][1]

    elif fast_level >= 1:
        raise Exception("Fast mode not yet working")
        results = _get_results(
            FetcherClass, services, kwargs, fast=fast_level, verbose=verbose
        )

    else:
        raise Exception("No mode specified.")

    if modes.get('report_services'):
        return used_services, consensus_results
    else:
        return consensus_results


def _prepare_consensus(FetcherClass, results):
    """
    Given a list of results, return a list that is simplified to make consensus
    determination possible. Returns two item tuple, first arg is simplified list,
    the second argument is a list of all services used in making these results.
    """
    # _get_results returns lists of 2 item list, first element is service, second is the returned value.
    # when determining consensus amoung services, only take into account values returned.
    if hasattr(FetcherClass, "strip_for_consensus"):
        to_compare = [
            FetcherClass.strip_for_consensus(value) for (fetcher, value) in results
        ]
    else:
        to_compare = [value for fetcher, value in results]

    return to_compare, [fetcher._successful_service for fetcher, values in results]

def _get_results(FetcherClass, services, kwargs, num_results=None, fast=0, verbose=False, timeout=None):
    """
    Does the fetching in multiple threads of needed. Used by paranoid and fast mode.
    """
    results = []

    if not num_results or fast:
        num_results = len(services)

    with futures.ThreadPoolExecutor(max_workers=len(services)) as executor:
        fetches = {}
        for service in services[:num_results]:
            tail = [x for x in services if x is not service]
            random.shuffle(tail)
            srv = FetcherClass(services=[service] + tail, verbose=verbose, timeout=timeout)
            fetches[executor.submit(srv.action, **kwargs)] = srv

        if fast == 1:
            raise NotImplementedError
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
            service = fetches[future]
            results.append([service, future.result()])

    return results

def _do_private_mode(FetcherClass, services, kwargs, random_wait_seconds, timeout, verbose):
    """
    Private mode is only applicable to address_balance, unspent_outputs, and
    historical_transactions. There will always be a list for the `addresses`
    argument. Each address goes to a random service. Also a random delay is
    performed before the external fetch for improved privacy.
    """
    addresses = kwargs.pop('addresses')
    results = {}

    with futures.ThreadPoolExecutor(max_workers=len(addresses)) as executor:
        fetches = {}
        for address in addresses:
            k = kwargs
            k['address'] = address
            random.shuffle(services)
            srv = FetcherClass(
                services=services, verbose=verbose, timeout=timeout or 5.0,
                random_wait_seconds=random_wait_seconds
            )
            # address is returned because balance needs to be returned
            # attached to the address. Other methods (get_transaction, unspent_outputs, etc)
            # do not need to be indexed by address. (upstream they are stripped out)
            fetches[executor.submit(srv.action, **k)] = (srv, address)

        to_iterate = futures.as_completed(fetches)

        for future in to_iterate:
            service, address = fetches[future]
            results[address] = future.result()

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
    if type(amount) in [float, int]:
        amount = "%.8f" % amount

    return int(amount.replace(".", '')) # avoiding float math

def get_optimal_services(crypto, type_of_service):
    from .crypto_data import crypto_data
    try:
        # get best services from curated list
        services = crypto_data[crypto.lower()]['services']
    except (KeyError, TypeError):
        raise CurrencyNotSupported("Unknown cryptocurrency symbol: %s" % crypto)

    try:
        s = services[type_of_service]
        if not s:
            raise KeyError()
        return s
    except KeyError:
        raise NoServicesDefined("No %s services defined for %s" % (type_of_service, crypto))


def get_magic_bytes(crypto):
    from .crypto_data import crypto_data
    try:
        pub_byte = crypto_data[crypto]['address_version_byte']
        priv_byte = crypto_data[crypto]['private_key_prefix']
        if priv_byte >= 128:
            priv_byte -= 128 #pybitcointools bug
        return pub_byte, priv_byte

    except KeyError:
        raise ValueError("Cryptocurrency symbol not found: %s" % crypto)

def make_standard_halfing_eras(start, interval, start_reward, halfing_func=None, total_eras=10):
    if not halfing_func:
        halfing_func = lambda x, y: y / float(2 ** (x))
    return [
    {
        'start': start + (era * interval) + 1,
        'end': start + ((era + 1) * interval),
        'reward': halfing_func(era, start_reward)
    } for era in range(0, total_eras)
]

def decompile_scriptPubKey(asm):
    """
    >>> decompile_scriptPubKey('OP_DUP OP_HASH160 cef3550ff9e637ddd120717d43fc21f8a563caf8 OP_EQUALVERIFY OP_CHECKSIG')
    '76a914cef3550ff9e637ddd120717d43fc21f8a563caf888ac'
    """
    asm = asm.split(" ")
    hex = ""
    if asm[0] == 'OP_DUP':
        hex += "76"
    if asm[1] == 'OP_HASH160':
        hex += 'a9'
    if len(asm[2]) == 40:
        hex += asm[2]
    if asm[3] == 'OP_EQUALVERIFY':
        hex += '88'
    if asm[4] == 'OP_CHECKSIG':
        hex += 'ac'
    return hex

def to_rawtx(tx):
    """
    Take a tx object in the moneywagon format and convert it to the format
    that pybitcointools's `serialize` funcion takes, then return in raw hex
    format.
    """
    if tx.get('hex'):
        return tx['hex']

    new_tx = {}

    locktime = tx.get('locktime', 0)
    new_tx['locktime'] = locktime
    new_tx['version'] = tx.get('version', 1)
    new_tx['ins'] = [
        {
            'outpoint': {'hash': str(x['txid']), 'index': x['n']},
            'script': str(x['scriptSig'].replace(' ', '')),
            'sequence': x.get('sequence', 0xFFFFFFFF if locktime == 0 else None)
        } for x in tx['inputs']
    ]

    new_tx['outs'] = [
        {
            'script': str(x['scriptPubKey']),
            'value': x['amount']
        } for x in tx['outputs']
    ]

    return serialize(new_tx)
