from __future__ import print_function

from .core import AutoFallback, enforce_service_mode
from .historical_price import Quandl
from .crypto_data import crypto_data


def get_current_price(crypto, fiat, service_mode='default', services=None, verbose=False):
    if service_mode.startswith('paranoid'):
        raise ValueError("paranoid mode not applicable for current price")

    if not services:
        services = crypto_data[crypto]['services']['current_price'] # get best services

    return enforce_service_mode(
        services, service_mode, CurrentPrice, [crypto, fiat], verbose
    )


def get_address_balance(crypto, address, service_mode='default', services=None, verbose=False):
    if not services:
        services = crypto_data[crypto]['services']['address_balance'] # get best services

    return enforce_service_mode(
        services, service_mode, AddressBalance, {'crypto': crypto, 'address': address}, verbose
    )


def get_historical_transactions(crypto, address, service_mode='default', services=None, verbose=False):
    if not services:
        services = crypto_data[crypto]['services']['historical_transactions'] # get best services

    return enforce_service_mode(
        services, service_mode, HistoricalTransactions, {'crypto': crypto, 'address': address}, verbose
    )


def get_unspent_outputs(crypto, address, service_mode='default', services=None, verbose=False):
    if not services:
        services = crypto_data[crypto]['services']['unspent_outputs'] # get best services
    return enforce_service_mode(
        services, service_mode, UnspentOutputs, {'crypto': crypto, 'address': address}, verbose
    )


def get_historical_price(crypto, fiat, date):
    return HistoricalPrice().get(crypto, fiat, date)


def push_tx(crypto, tx_hex, service_mode='default', verbose=False, services=None):
    if not services:
        services = crypto_data[crypto]['services']['push_tx'] # get best services
    return enforce_service_mode(
        services, service_mode, PushTx, {'crypto': crypto, 'tx_hex': tx_hex}, verbose
    )

def get_block(crypto, block_number='', block_hash='', latest=False, service_mode='default', verbose=False, services=None):
    if not services:
        services = crypto_data[crypto]['services']['get_block'] # get best services
    kwargs = dict(crypto=crypto, block_number=block_number, block_hash=block_hash, latest=latest)
    return enforce_service_mode(
        services, service_mode, GetBlock, kwargs, verbose
    )


def get_optimal_fee(crypto, tx_bytes, acceptable_block_delay):
    return OptimalFee().get(crypto, tx_bytes, acceptable_block_delay)


class OptimalFee(AutoFallback):
    service_method_name = "get_optimal_fee"

    def get(self, crypto, tx_bytes, acceptable_block_delay=0):
        crypto = crypto.lower()
        return self._try_each_service(crypto, tx_bytes, acceptable_block_delay)

    def no_service_msg(self, crypto, tx_bytes, acceptable_block_delay):
        return "Could not get optimal fee for: %s" % crypto

class GetBlock(AutoFallback):
    service_method_name = 'get_block'

    def get(self, crypto, block_number='', block_hash='', latest=False):
        if sum([bool(block_number), bool(block_hash), bool(latest)]) != 1:
            raise ValueError("Only one of `block_hash`, `latest`, or `block_number` allowed.")
        return self._try_each_service(
            crypto, block_number=block_number, block_hash=block_hash, latest=latest
        )

    def no_service_msg(self, crypto, block_number='', block_hash='', latest=False):
        return "Could not get %s block: %s%s%s" % (
            crypto, block_number, block_hash, 'latest' if latest else ''
        )

class HistoricalTransactions(AutoFallback):
    service_method_name = 'get_transactions'

    def get(self, crypto, address):
        return self._try_each_service(crypto, address)

    def no_service_msg(self, crypto, address):
        return "Could not get transactions for: %s" % crypto


class UnspentOutputs(AutoFallback):
    service_method_name = 'get_unspent_outputs'

    def get(self, crypto, address):
        return self._try_each_service(crypto, address)

    def no_service_msg(self, crypto, address):
        return "Could not get unspent outputs for: %s" % crypto


class CurrentPrice(AutoFallback):
    service_method_name = 'get_current_price'

    def get(self, crypto, fiat):
        if crypto.lower() == fiat.lower():
            return (1.0, 'math')

        return self._try_each_service(crypto, fiat)

    def no_service_msg(self, crypto, fiat):
        return "Can not find price for %s->%s" % (crypto, fiat)


class AddressBalance(AutoFallback):
    service_method_name = "get_balance"

    def get(self, crypto, address, confirmations=1):
        return self._try_each_service(crypto, address, confirmations)

    def no_service_msg(self, crypto, address, confirmations=1):
        return "Could not get confirmed address balance for: %s" % crypto


class PushTx(AutoFallback):
    service_method_name = "push_tx"

    def push(self, crypto, tx_hex):
        return self._try_each_service(crypto, tx_hex)

    def no_service_msg(self, crypto, hex):
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
