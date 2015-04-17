from pybitcointools import history, mktx, signall

def from_unit_to_satoshi(value, unit):
    """
    Convert a value to satoshis. units can be any fiat currency
    """
    from moneywagon import get_current_price
    if not unit or unit == 'satoshi':
        return value
    if unit == 'bitcoin' or unit == 'btc':
        return value * 1e8

    # assume fiat currency that we can convert
    convert = get_current_price('btc', unit)[0]
    return int(value / convert * 1e8)


class Transaction(object):
    def __init__(self, currency, hex=None, inputs=None):
        if not currency.lower() == 'btc':
            raise ValueError("Transaction only supports BTC at this time")

        self.currency = currency
        self.fee_satoshi = 10000
        self.outs = []
        self.ins = []
        if hex:
            self.hex = hex

    def add_input(self, address, private_key, amount='all'):
        self.private_key = private_key
        self.change_address = address

        total_added = 0
        for o in history(address):
            if (amount == 'all' or total_added < amount) and not o.get('spend'):
                self.ins.append(o)
                total_added += o['value']

    def total_input_satoshis(self):
        """
        Add up all the satoshis coming from all input tx's.
        """
        return sum([x['value'] for x in self.ins])

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
        self.fee_satoshi = from_unit_to_satoshi(value, unit)

    def get_hex(self):
        """
        Given all the data the user has given so far, make the hex using pybitcointools
        """
        total_ins = self.total_input_satoshis()
        total_outs = sum([x['value'] for x in self.outs])
        change_satoshi = total_ins - (total_outs + self.fee_satoshi)

        if change_satoshi < 0:
            raise ValueError("Input amount must be more than all Output amounts. You need more bitcoin.")

        tx = mktx(self.ins, self.outs + [{'address': self.change_address, 'value': change_satoshi}])
        tx = signall(tx, self.private_key)

        return tx

    def push(self):
        from moneywagon import push_tx
        return push_tx(self.currency, self.get_hex())
