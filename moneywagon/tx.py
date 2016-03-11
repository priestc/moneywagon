from moneywagon import (
    get_unspent_outputs, CurrentPrice, get_optimal_fee, PushTx,
)
from moneywagon.core import get_optimal_services, get_magic_bytes
from bitcoin import mktx, sign, pubtoaddr, privtopub
from .crypto_data import crypto_data

class Transaction(object):
    def __init__(self, crypto, hex=None, verbose=False):
        if crypto.lower() in ['nxt']:
            raise NotImplementedError("%s not yet supported" % crypto.upper())

        self.change_address = None
        self.crypto = crypto
        self.fee_satoshi = None
        self.outs = []
        self.ins = []

        self.verbose = verbose

        services = get_optimal_services(self.crypto, 'current_price')
        self.price_getter = CurrentPrice(services=services, verbose=verbose)

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
        convert = self.price_getter.action(self.crypto, unit)
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

    def _get_utxos(self, address, services, **modes):
        """
        Using the service fallback engine, get utxos from remote service.
        """
        return get_unspent_outputs(
            self.crypto, address, services=services,
            **modes
        )

    def private_key_to_address(self, pk):
        """
        Convert a private key (in hex format) into an address.
        """
        pub = privtopub(pk)
        pub_byte, priv_byte = get_magic_bytes(self.crypto)

        if priv_byte >= 128:
            priv_byte -= 128 #pybitcointools bug

        return pubtoaddr(pub, pub_byte)

    def add_inputs(self, private_key=None, address=None, amount='all', max_ins=None, password=None, services=None, **modes):
        """
        Make call to external service to get inputs from an address and/or private_key.
        `amount` is the amount of [currency] worth of inputs (in satoshis) to add from
        this address. Pass in 'all' (the default) to use *all* inputs found for this address.
         Returned is the number of units (in satoshis) that were added as inputs to this tx.
        """
        if private_key:
            if private_key.startswith('6P'):
                if not password:
                    raise Exception("Password required for BIP38 encoded private keys")
                from .bip38 import Bip38EncryptedPrivateKey
                private_key = Bip38EncryptedPrivateKey(self.crypto, private_key).decrypt(password)

            address_from_priv = self.private_key_to_address(private_key)
            if address and address != address_from_priv:
                raise Exception("Invalid Private key")
            address = address_from_priv
            self.change_address = address

        if not services:
            services = get_optimal_services(self.crypto, 'unspent_outputs')

        total_added_satoshi = 0
        ins = 0
        for utxo in self._get_utxos(address, services, **modes):
            if max_ins and ins >= max_ins:
                break
            if (amount == 'all' or total_added_satoshi < amount):
                ins += 1
                self.ins.append(
                    dict(input=utxo, private_key=private_key)
                )
                total_added_satoshi += utxo['amount']

        return total_added_satoshi, ins

    def total_input_satoshis(self):
        """
        Add up all the satoshis coming from all input tx's.
        """
        just_inputs = [x['input'] for x in self.ins]
        return sum([x['amount'] for x in just_inputs])

    def select_inputs(self, amount):
      '''Maximize transaction priority. Select the oldest inputs,
      that are sufficient to cover the spent amount. Then,
      remove any unneeded inputs, starting with
      the smallest in value.
      Returns sum of amounts of inputs selected'''
      sorted_txin = sorted(self.ins, key=lambda x:-x['input']['confirmations'])
      total_amount = 0
      for (idx, tx_in) in enumerate(sorted_txin):
        total_amount += tx_in['input']['amount']
        if (total_amount >= amount):
          break
      sorted_txin = sorted(sorted_txin[:idx+1], key=lambda x:x['input']['amount'])
      for (idx, tx_in) in enumerate(sorted_txin):
        value = tx_in['input']['amount']
        if (total_amount - value < amount):
          break
        else:
          total_amount -= value
      self.ins = sorted_txin[idx:]
      return total_amount

    def add_output(self, address, value, unit='satoshi'):
        """
        Add an output (a person who will receive funds via this tx).
        If no unit is specified, satoshi is implied.
        """
        value_satoshi = self.from_unit_to_satoshi(value, unit)

        if self.verbose:
            print("Adding output of: %s satoshi (%.8f)" % (
                value_satoshi, (value_satoshi / 1e8)
            ))

        self.outs.append({
            'address': address,
            'value': value_satoshi
        })

    def fee(self, value=None, unit='satoshi'):
        """
        Set the miner fee, if unit is not set, assumes value is satoshi.
        If using 'optimal', make sure you have already added all outputs.
        """
        convert = None
        if not value:
            # no fee was specified, use $0.02 as default.
            convert = self.price_getter.action(self.crypto, "usd")
            self.fee_satoshi = int(0.02 / convert * 1e8)
            verbose = "Using default fee of:"

        elif value == 'optimal':
            self.fee_satoshi = get_optimal_fee(
                self.crypto, self.estimate_size(), verbose=self.verbose
            )
            verbose = "Using optimal fee of:"
        else:
            self.fee_satoshi = self.from_unit_to_satoshi(value, unit)
            verbose = "Using manually set fee of:"

        if self.verbose:
            if not convert:
                convert = self.price_getter.action(self.crypto, "usd")
            fee_dollar = convert * self.fee_satoshi / 1e8
            print(verbose + " %s satoshis ($%.2f)" % (self.fee_satoshi, fee_dollar))

    def estimate_size(self):
        """
        Estimate how many bytes this transaction will be by countng inputs
        and outputs.
        Formula taken from: http://bitcoin.stackexchange.com/a/3011/18150
        """
        # if there are no outs use 1 (because the change will be an out)
        outs = len(self.outs) or 1
        return outs * 34 + 148 * len(self.ins) + 10

    def get_hex(self, signed=True):
        """
        Given all the data the user has given so far, make the hex using pybitcointools
        """
        total_ins_satoshi = self.total_input_satoshis()
        if total_ins_satoshi == 0:
            raise ValueError("Can't make transaction, there are zero inputs")

        # Note: there can be zero outs (sweep or coalesc transactions)
        total_outs_satoshi = sum([x['value'] for x in self.outs])

        if not self.fee_satoshi:
            self.fee() # use default of $0.02

        change_satoshi = total_ins_satoshi - (total_outs_satoshi + self.fee_satoshi)

        if change_satoshi < 0:
            raise ValueError(
                "Input amount (%s) must be more than all output amounts (%s) plus fees (%s). You need more %s."
                % (total_ins_satoshi, total_outs_satoshi, self.fee_satoshi, self.crypto.upper())
            )

        ins = [x['input'] for x in self.ins]

        if change_satoshi > 0:
            if self.verbose:
                print("Adding change address of %s satoshis to %s" % (change_satoshi, self.change_address))
            change = [{'value': change_satoshi, 'address': self.change_address}]
        else:
            change = [] # no change ?!
            if self.verbose: print("Inputs == Outputs, no change address needed.")

        tx = mktx(ins, self.outs + change)

        if signed:
            for i, input_data in enumerate(self.ins):
                if not input_data['private_key']:
                    raise Exception("Can't sign transaction, missing private key for input %s" % i)
                tx = sign(tx, i, input_data['private_key'])

        return tx

    def push(self, services=None, redundancy=1):
        if not services:
            services = get_optimal_services(self.crypto, "push_tx")

        self.pushers = []
        pusher = PushTx(services=services, verbose=self.verbose)
        results = [pusher.action(self.crypto, self.get_hex())]

        try:
            for service in services[1:redundancy-1]:
                pusher = PushTx(services=[service], verbose=self.verbose)
                results.append(self.pusher.action(self.crypto, self.get_hex()))
                self.pushers.append(pusher)
        except:
            raise Exception("Partial push. Some services returned success, some failed.")

        return results
