from moneywagon import (
    get_unspent_outputs, get_current_price, get_optimal_fee, push_tx
)
from bitcoin import mktx, sign

def from_unit_to_satoshi(value, unit):
    """
    Convert a value to satoshis. units can be any fiat currency
    """
    if not unit or unit == 'satoshi':
        return value
    if unit == 'bitcoin' or unit == 'btc':
        return value * 1e8

    # assume fiat currency that we can convert
    convert = get_current_price('btc', unit)[0]
    return int(value / convert * 1e8)


class Transaction(object):
    def __init__(self, crypto, hex=None, paranoid=1, utxo_services=None, pushtx_services=None):
        if not crypto.lower() == 'btc':
            raise ValueError("Transaction only supports BTC at this time")

        self.paranoid = paranoid
        self.crypto = crypto
        self.fee_satoshi = 10000
        self.outs = []
        self.ins = []

        self.utxo_services = utxo_services or []
        self.pushtx_services = pushtx_services or []

        if hex:
            self.hex = hex

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

    def _get_utxos(self, address):
        """
        Using the service fallback engine, get utxos from remote service.
        """
        return get_unspent_outputs(
            self.crypto, address, services=self.utxo_services, paranoid=self.paranoid
        )

    def add_inputs_from_address(self, address, private_key=None, amount='all'):
        """
        Make call to external service to get inputs from an address.
        `amount` is the amount of [currency] worth of inputs to add from this address.
          pass in 'all' (the default) to use *all* inputs found for this address.
        """
        self.private_key = private_key
        self.change_address = address

        total_added = 0
        ins = []
        for utxo in self._get_utxos(address):
            if (amount == 'all' or total_added < amount):
                self.ins.append(
                    dict(input=utxo, private_key=private_key)
                )
                total_added += utxo['value']

    def total_input_satoshis(self):
        """
        Add up all the satoshis coming from all input tx's.
        """
        just_inputs = [x['input'] for x in self.ins]
        return sum([x['value'] for x in just_inputs])

    def add_output(self, address, value, unit=None):
        """
        Add an output (a person who will receive funds via this tx)
        """
        value_satoshi = from_unit_to_satoshi(value, unit)
        self.outs.append({
            'address': address,
            'value': value_satoshi
        })

    def fee(self, value, unit=None):
        """
        Set the miner fee, if unit is not set, assumes value is satoshi
        """
        if value == 'optimal':
            self.fee_satoshi = 'optimal'
        else:
            self.fee_satoshi = from_unit_to_satoshi(value, unit)

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
        total_ins = self.total_input_satoshis()
        total_outs = sum([x['value'] for x in self.outs])

        fee = self.fee_satoshi
        if fee == 'optimal':
            # makes call to external service to get optimal fee
            fee = get_optimal_fee(self.currency, self.estimate_size(), 0)

        change_satoshi = total_ins - (total_outs + fee)

        if change_satoshi < 0:
            raise ValueError("Input amount must be more than all Output amounts. You need more bitcoin.")

        ins = [x['input'] for x in self.ins]

        tx = mktx(ins, self.outs + [{'address': self.change_address, 'value': change_satoshi}])

        if signed:
            for i, private_key in self.ins:
                if not private_key:
                    raise Exception("Can't sign transaction, missing private key")
                tx = sign(tx, private_key, i)

        return tx

    def push(self):
        return push_tx(self.currency, self.get_hex(), services=self.pushtx_services)
