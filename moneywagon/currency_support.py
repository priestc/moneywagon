import itertools
import collections
import binascii

from moneywagon.services import get_service
from moneywagon.crypto_data import crypto_data
from moneywagon import ALL_SERVICES

class CurrencySupport(object):
    support_categories = {
        'address': ['address_form', 'private_key_form'],
        'transaction': [ 'transaction_form', 'transaction_hash_algo', 'script_hash_algo'],
        'block': ['header_hash_algo'],
    }
    project_attributes = {
        'altcore': {
            'address_form': ('sha256-check', 'groestl-check'),
            'private_key_form': ('btc', ),
            'transaction_form': ('btc', ),
            'transaction_hash_algo': ('double-sha256', 'single-sha256'),
            'script_hash_algo': ('double-sha256', 'groestl'),
            'header_hash_algo': ('double-sha256', 'groestl')
        },
        'moneywagon': {
            'address_form': ('sha256-check', ),
            'private_key_form': ('btc', ),
            'transaction_form': ('btc', ),
            'transaction_hash_algo': ('double-sha256', ),
            'script_hash_algo': ('double-sha256', ),
            'header_hash_algo': ('double-sha256', )
        },
    }

    def __init__(self, verbose=False):
        self.verbose = verbose

    @property
    def sorted_crypto_data(self):
        return sorted(crypto_data.items(), key=lambda x: x[1]['name'])

    def is_all_supported(self, crypto_data_item, project, level):
        if level == 'full':
            fields_to_check = list(itertools.chain.from_iterable(self.support_categories.values()))
        else:
            fields_to_check = self.support_categories[level]

        for field, supported in self.project_attributes[project].items():
            value = crypto_data_item.get(field)
            if field not in fields_to_check:
                continue
            if value is not None and value not in supported:
                return False
        return True

    def supported_currencies(self, project='moneywagon', level="full"):
        """
        Returns a list of all currencies that are supported by the passed in project.
        and support level. Support level can be: "block", "transaction", "address"
        or "full".
        """
        ret = []
        if project == 'multiexplorer-wallet':
            for currency, data in self.sorted_crypto_data:
                if not data.get("bip44_coin_type"):
                    continue
                if len(data.get('services', {}).get("push_tx", [])) < 1:
                    continue
                if len(data.get('services', {}).get("historical_transactions", [])) < 1:
                    continue
                if len(data.get('services', {}).get("single_transaction", [])) < 1:
                    continue
                if len(data.get('services', {}).get("unspent_outputs", [])) < 1:
                    continue
                ret.append(currency)

            altcore_tx = self.supported_currencies('altcore', level="transaction")
            return [x for x in ret if x in altcore_tx]

        for symbol, data in self.sorted_crypto_data:
            if symbol == '': # template
                continue
            if self.is_all_supported(data, project, level):
                ret.append(symbol)
        return ret

    def not_supported_currencies(self, project='moneywagon', level="full"):
        """
        Returns a list of all currencies that are defined in moneywagon, by not
        supported by the passed in project and support level. Support level can
        be: "block", "transaction", "address" or "full".
        """
        supported = self.supported_currencies(project, level)
        ret = []
        for symbol, data in self.sorted_crypto_data:
            if symbol == '': # template
                continue
            if symbol not in supported:
                ret.append(symbol)
        return ret

    def altcore_data(self):
        """
        Returns the crypto_data for all currencies defined in moneywagon that also
        meet the minimum support for altcore. Data is keyed according to the
        bitcore specification.
        """
        ret = []
        for symbol in self.supported_currencies(project='altcore', level="address"):
            data = crypto_data[symbol]
            priv = data.get('private_key_prefix')
            pub = data.get('address_version_byte')
            hha = data.get('header_hash_algo')
            shb = data.get('script_hash_byte')

            supported = collections.OrderedDict()
            supported['name'] = data['name']
            supported['alias'] = symbol

            if pub is not None:
                supported['pubkeyhash'] = int(pub)
            if priv:
                supported['privatekey'] = priv
            supported['scripthash'] = shb if shb else 5
            if 'transaction_form' in data:
                supported['transactionForm'] = data['transaction_form']
            if 'private_key_form' in data:
                supported['privateKeyForm'] = data['private_key_form']
            #if 'message_magic' in data and data['message_magic']:
            #    supported['networkMagic'] = '0x%s' % binascii.hexlify(data['message_magic'])
            supported['port'] = data.get('port') or None
            if hha not in (None, 'double-sha256'):
                supported['headerHashAlgo'] = hha
            if data.get('script_hash_algo', 'double-sha256') not in (None, 'double-sha256'):
                supported['scriptHashAlgo'] = data['script_hash_algo']
            if data.get('transaction_hash_algo', 'double-sha256') not in (None, 'double-sha256'):
                supported['transactionHashAlgo'] = data['transaction_hash_algo']
            if data.get('seed_nodes'):
                supported['dnsSeeds'] = data['seed_nodes']

            ret.append(supported)

        return ret


def service_support(method=None, service=None, timeout=0.1, verbose=False):
    possible_args = {
        'get_current_price': ['btc', 'usd'],
        'get_balance': ['btc', '123445'],
        'get_orderbook': ['btc', 'usd'],
        'push_tx': ['btc', '23984729847298'],
        'make_order': ['btc', 'usd', 9999999999, 99999999, "sell"],
        'get_exchange_balance': ['btc'],
        'get_deposit_address': ['btc'],
        'initiate_withdraw': ['btc', 999999999999, '123456'],
    }
    matched = []

    def determine_support(s, method):
        try:
            getattr(s, method)(*possible_args[method])
        except NotImplementedError:
            if verbose:
                print("not implemented", s.name)
            return False
        except Exception as exc:
            if verbose:
                print ("implemented", s.name, exc, str(exc))
            return True
        return True

    if method:
        for Service in ALL_SERVICES:
            s = Service(timeout=timeout)
            if determine_support(s, method):
                matched.append(s.name)

    elif service:
        s = get_service(name=service)(timeout=timeout)
        for method in possible_args:
            if determine_support(s, method):
                matched.append(method)

    return matched
