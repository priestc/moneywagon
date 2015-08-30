from moneywagon import (
    get_unspent_outputs, CurrentPrice, get_optimal_fee, PushTx
)
from bitcoin import mktx, sign
from .crypto_data import crypto_data


class Transaction(object):
    def __init__(self, crypto, hex=None, paranoid=1, verbose=False):
        if crypto.lower() in ['nxt']:
            raise NotImplementedError("%s not yet supported" % crypto.upper())

        self.paranoid = paranoid
        self.crypto = crypto
        self.fee_satoshi = None
        self.outs = []
        self.ins = []
        self.verbose = verbose

        self.price_getter = CurrentPrice(verbose=verbose)

        if hex:
            self.hex = hex

    def from_unit_to_satoshi(self, value, unit='satoshi'):
        """
        Convert a value to satoshis. units can be any fiat currency.
        By default the unit is satoshi.
        """
        if not unit or unit == 'satoshi':
            return value
        if unit == 'bitcoin' or unit == 'btc':
            return value * 1e8

        # assume fiat currency that we can convert
        convert = self.price_getter.get(self.crypto, unit)[0]
        return int(value / convert * 1e8)

    def add_raw_inputs(self, inputs, private_key=None):
        """
        Add a set of utxo's to this transaction. This method is better to use if you
        want more fine control of which inputs get added to a transaction.
        `inputs` is a list of "unspent outputs" (they were 'outputs' to previous transactions,
          and 'inputs' to subsiquent transactions).

        `private_key` - All inputs will be signed by the passed in private key.
        """
        for i in inputs:
            self.ins.append(dict(input=i, private_key=private_key))
            self.change_address = i['address']

    def _get_utxos(self, address, services):
        """
        Using the service fallback engine, get utxos from remote service.
        """
        return get_unspent_outputs(
            self.crypto, address, services=services,
            paranoid=self.paranoid, verbose=self.verbose
        )

    def add_inputs_from_address(self, address, private_key=None, amount='all', services=None):
        """
        Make call to external service to get inputs from an address.
        `amount` is the amount of [currency] worth of inputs to add from this address.
          pass in 'all' (the default) to use *all* inputs found for this address.
        """
        self.private_key = private_key
        self.change_address = address

        total_added = 0
        ins = []
        for utxo in self._get_utxos(address, services or []):
            if (amount == 'all' or total_added < amount):
                self.ins.append(
                    dict(input=utxo, private_key=private_key)
                )
                total_added += utxo['amount']

    def total_input_satoshis(self):
        """
        Add up all the satoshis coming from all input tx's.
        """
        just_inputs = [x['input'] for x in self.ins]
        return sum([x['amount'] for x in just_inputs])

    def add_output(self, address, value, unit='satoshi'):
        """
        Add an output (a person who will receive funds via this tx).
        If no unit is specified, satoshi is implied.
        """
        value_satoshi = self.from_unit_to_satoshi(value, unit)

        if self.verbose:
            print(
                "Adding output of: %s satoshi (%.8f)" % (
                    value_satoshi, (value_satoshi / 1e8)
                )
            )

        self.outs.append({
            'address': address,
            'value': value_satoshi
        })

    def fee(self, value, unit='satoshi'):
        """
        Set the miner fee, if unit is not set, assumes value is satoshi
        """
        if value == 'optimal':
            self.fee_satoshi = 'optimal'
        else:
            self.fee_satoshi = self.from_unit_to_satoshi(value, unit)

    def estimate_size(self):
        """
        Estimate how many bytes this transaction will be by countng inputs
        and outputs.
        Formula taken from: http://bitcoin.stackexchange.com/a/3011/18150
        """
        return len(self.outs) * 148 + 34 * len(self.ins) + 10

    def get_hex(self, signed=True):
        """
        Given all the data the user has given so far, make the hex using pybitcointools
        """
        total_ins_satoshi = self.total_input_satoshis()
        total_outs_satoshi = sum([x['value'] for x in self.outs])

        fee_satoshi = self.fee_satoshi
        if fee_satoshi == 'optimal':
            # makes call to external service to get optimal fee
            fee_satoshi = get_optimal_fee(self.crypto, self.estimate_size(), 0, verbose=self.verbose)

        if not fee_satoshi:
            # no fee was specified, use $0.02 as default.
            convert = self.price_getter.get(self.crypto, "usd")[0]
            fee_satoshi = int(0.02 * convert * 1e8)
            if self.verbose: print("Using default fee of %s satoshi ($0.02)" % fee_satoshi)

        change_satoshi = total_ins_satoshi - (total_outs_satoshi + fee_satoshi)

        if change_satoshi < 0:
            raise ValueError(
                "Input amount must be more than all Output amounts. You need more %s." % self.crypto
            )

        ins = [x['input'] for x in self.ins]

        tx = mktx(ins, self.outs + [{'address': self.change_address, 'value': change_satoshi}])

        if signed:
            for i, input_data in enumerate(self.ins):
                if not input_data['private_key']:
                    raise Exception("Can't sign transaction, missing private key")
                tx = sign(tx, i, input_data['private_key'])

        return tx

    def push(self, services=None):
        self.pusher = PushTx(verbose=self.verbose, services=services or [])
        return self.pusher.get(self.crypto, self.get_hex())
