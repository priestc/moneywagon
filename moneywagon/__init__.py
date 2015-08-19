from __future__ import print_function

from .core import AutoFallback, enforce_service_mode
from .historical_price import Quandl
from .crypto_data import crypto_data
from bitcoin import sha256, pubtoaddr, privtopub, encode_privkey

def _get_optimal_services(crypto, type_of_service):
    try:
        # get best services from curated list
        return crypto_data[crypto]['services'][type_of_service]
    except KeyError:
        raise ValueError("Invalid cryptocurrency symbol: %s" % crypto)

def _get_magic_bytes(crypto):
    try:
        return (
            crypto_data[crypto]['address_version_byte'],
            crypto_data[crypto]['private_key_prefix']
        )

    except KeyError:
        raise ValueError("Invalid cryptocurrency symbol: %s" % crypto)

def get_current_price(crypto, fiat, services=None, **modes):
    if not services:
        services = _get_optimal_services(crypto, 'current_price')

    return enforce_service_mode(
        services, CurrentPrice, {'crypto': crypto, 'fiat': fiat}, modes=modes
    )


def get_address_balance(crypto, address, services=None, **modes):
    if not services:
        services = _get_optimal_services(crypto, 'address_balance')

    return enforce_service_mode(
        services, AddressBalance, {'crypto': crypto, 'address': address}, modes=modes
    )


def get_historical_transactions(crypto, address, services=None, **modes):
    if not services:
        services = _get_optimal_services(crypto, 'historical_transactions')

    return enforce_service_mode(
        services, HistoricalTransactions, {'crypto': crypto, 'address': address}, modes=modes
    )


def get_unspent_outputs(crypto, address, services=None, **modes):
    if not services:
        services = _get_optimal_services(crypto, 'unspent_outputs')
    return enforce_service_mode(
        services, UnspentOutputs, {'crypto': crypto, 'address': address}, modes=modes
    )


def get_historical_price(crypto, fiat, date):
    """
    Only one service is defined fr geting historical price, so no fetching modes
    are needed.
    """
    return HistoricalPrice().get(crypto, fiat, date)


def push_tx(crypto, tx_hex, verbose=False, services=None, **modes):
    if not services:
        services = _get_optimal_services(crypto, 'push_tx')
    return enforce_service_mode(
        services, PushTx, {'crypto': crypto, 'tx_hex': tx_hex}, modes=modes
    )

def get_block(crypto, block_number='', block_hash='', latest=False, services=None, **modes):
    if not services:
        services = _get_optimal_services(crypto, 'get_block')
    kwargs = dict(crypto=crypto, block_number=block_number, block_hash=block_hash, latest=latest)
    return enforce_service_mode(
        services, GetBlock, kwargs, modes=modes
    )


def get_optimal_fee(crypto, tx_bytes, acceptable_block_delay, verbose=False):
    return OptimalFee(verbose=verbose).get(crypto, tx_bytes, acceptable_block_delay)


def generate_address(crypto, seed):
    """
    Generate a private key and publickey for any currency, given a seed.
    That seed can be random, or a brainwallet phrase.
    """
    pub_byte, priv_byte = _get_magic_bytes(crypto)
    priv = sha256(seed)
    pub = privtopub(priv)

    if priv_byte >= 128:
        priv_byte -= 128 #pybitcointools bug

    return {
        'address': pubtoaddr(pub, pub_byte),
        'private_hex': priv,
        'private_wif': encode_privkey(priv, 'wif', vbyte=priv_byte)
    }

class OptimalFee(AutoFallback):

    def get(self, crypto, tx_bytes, acceptable_block_delay=0):
        crypto = crypto.lower()
        return self._try_each_service("get_optimal_fee", crypto, tx_bytes, acceptable_block_delay)

    def no_service_msg(self, crypto, tx_bytes, acceptable_block_delay):
        return "Could not get optimal fee for: %s" % crypto

class GetBlock(AutoFallback):

    def get(self, crypto, block_number='', block_hash='', latest=False):
        if sum([bool(block_number), bool(block_hash), bool(latest)]) != 1:
            raise ValueError("Only one of `block_hash`, `latest`, or `block_number` allowed.")
        return self._try_each_service(
            'get_block', crypto, block_number=block_number, block_hash=block_hash, latest=latest
        )

    def no_service_msg(self, crypto, block_number='', block_hash='', latest=False):
        return "Could not get %s block: %s%s%s" % (
            crypto, block_number, block_hash, 'latest' if latest else ''
        )

    @classmethod
    def strip_for_consensus(self, results):
        stripped = []
        for result in results:
            stripped.append(
                "[hash: %s, number: %s, size: %s]" % (
                    result['hash'], result['block_number'], result['size']
                )
            )
        return stripped

class HistoricalTransactions(AutoFallback):

    def get(self, crypto, address):
        return self._try_each_service('get_transactions', crypto, address)

    def no_service_msg(self, crypto, address):
        return "Could not get transactions for: %s" % crypto

    @classmethod
    def strip_for_consensus(cls, results):
        stripped = []
        for result in results:
            result.sort(key=lambda x: x['date'])
            stripped.append(
                ", ".join(
                    ["[id: %s, amount: %s]" % (x['txid'], x['amount']) for x in result]
                )
            )
        return stripped

class UnspentOutputs(AutoFallback):

    def get(self, crypto, address):
        return self._try_each_service('get_unspent_outputs', crypto=crypto, address=address)

    def no_service_msg(self, crypto, address):
        return "Could not get unspent outputs for: %s" % crypto

    @classmethod
    def strip_for_consensus(cls, results):
        stripped = []
        for result in results:
            result.sort(key=lambda x: x['output'])
            stripped.append(
                ", ".join(
                    ["[output: %s, value: %s]" % (x['output'], x['amount']) for x in result]
                )
            )
        return stripped


class CurrentPrice(AutoFallback):

    def get(self, crypto, fiat):
        if crypto.lower() == fiat.lower():
            return (1.0, 'math')

        return self._try_each_service('get_current_price', crypto=crypto, fiat=fiat)

    def no_service_msg(self, crypto, fiat):
        return "Can not find price for %s->%s" % (crypto, fiat)


class AddressBalance(AutoFallback):

    def get(self, crypto, address=None, addresses=None, confirmations=1):
        kwargs = dict(crypto=crypto, confirmations=confirmations)

        if address:
            method_name = "get_balance"
            kwargs['address'] = address

        if addresses:
            method_name = "get_balance_multi"
            kwargs['addresses'] = addresses

        return self._try_each_service(method_name, **kwargs)

    def no_service_msg(self, crypto, address, confirmations=1):
        return "Could not get confirmed address balance for: %s" % crypto


class PushTx(AutoFallback):

    def get(self, crypto, tx_hex):
        return self._try_each_service("push_tx", crypto=crypto, tx_hex=tx_hex)

    def no_service_msg(self, crypto, tx_hex):
        return "Could not push this %s transaction." % crypto


class HistoricalPrice(object):
    """
    This one doesn't inherit from AutoFallback because there is only one
    historical price API service at the moment.
    """
    def __init__(self, responses=None, verbose=False):
        self.service = Quandl(responses, verbose=verbose)

    def get(self, crypto, fiat, at_time):
        crypto = crypto.lower()
        fiat = fiat.lower()

        if crypto != 'btc' and fiat != 'btc':
            # two external requests and some math is going to be needed.
            from_btc, source1, date1 = self.service.get_historical(crypto, 'btc', at_time)
            to_altcoin, source2, date2 = self.service.get_historical('btc', fiat, at_time)
            return (from_btc * to_altcoin), "%s x %s" % (source1, source2), date1
        else:
            return self.service.get_historical(crypto, fiat, at_time)

    @property
    def responses(self):
        return self.service.responses
