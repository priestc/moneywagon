from __future__ import print_function

import random
from .crypto_data import crypto_data
from moneywagon import get_block, push_tx, get_single_transaction, watch_mempool
from .core import to_rawtx
from moneywagon.services import BitpayInsight, ChainSo, LocalBitcoinsChain, BlockDozer

class NetworkReplay(object):
    def __init__(self, source, destination, block_fetcher=None, verbose=False):
        """
        `block_fetcher` is a callable that will return a block.
        source is cryptocurrency network we get transactions from.
        destination is cryptocurrency network we will replay transactions to.
        """
        self.source = source
        self.destination = destination
        self.block_fetcher = block_fetcher
        self.verbose = verbose

        parent_currency, self.parent_fork_block = crypto_data[source.lower()].get('forked_from') or [None, 0]
        child_currency, self.child_fork_block = crypto_data[destination.lower()].get('forked_from') or [None, 0]

        if not parent_currency and not child_currency:
            raise Exception("Networks %s and %s are not forks of one another." % (
                source.upper(), destination.upper()
            ))

        if source.lower() == 'btc':
            self.pusher = BlockDozer(verbose=verbose)
            self.tx_fetcher = random.choice([BitpayInsight, ChainSo, LocalBitcoinsChain])(verbose=verbose)
        elif source.lower() == 'bch':
            self.pusher = random.choice(crypto_data['btc']['services']['push_tx'])(verbose=verbose)
            self.tx_fetcher = BlockDozer(verbose=verbose)
        else:
            raise Exception("Only BTC and BCH are currently supported")


    def replay_block(self, block_to_replay, limit=5):
        """
        Replay all transactions in parent currency to passed in "source" currency.
        Block_to_replay can either be an integer or a block object.
        """

        if block_to_replay == 'latest':
            if self.verbose:
                print("Getting latest %s block header" % source.upper())
            block = get_block(self.source, latest=True, verbose=self.verbose)
            if self.verbose:
                print("Latest %s block is #%s" % (self.source.upper(), block['block_number']))
        else:
            blocknum = block_to_replay if type(block_to_replay) == int else block_to_replay['block_number']
            if blocknum < self.parent_fork_block or blocknum < self.child_fork_block:
                raise Exception("Can't replay blocks mined before the fork")

        if type(block_to_replay) is not dict:
            if self.verbose:
                print("Getting %s block header #%s" % (self.source.upper(), block_to_replay))
            block = get_block(self.source, block_number=int(block_to_replay), verbose=self.verbose)
        else:
            block = block_to_replay

        if self.verbose:
            print("Using %s for pushing to %s" % (self.pusher.name, self.destination.upper()))
            print("Using %s for getting %s transactions" % (self.tx_fetcher.name, self.source.upper()))
            print("Finished getting block header,", len(block['txids']), "transactions in block, will replay", (limit or "all of them"))

        results = []
        enforced_limit = (limit or len(block['txids']))

        for i, txid in enumerate(block['txids'][:enforced_limit]):
            print("outside", txid)
            self._replay_tx(txid, i)


    def _replay_tx(self, txid, i=None):
        if self.block_fetcher:
            transaction = self.block_fetcher(currency=self.source, txid=txid)
        else:
            transaction = self.tx_fetcher.get_single_transaction(self.source, txid=txid)

        first_input = transaction['inputs'][0]
        if first_input.get('coinbase') or first_input.get("addresses") == "coinbase":
            return # no point trying to replay coinbases.

        raw_tx = to_rawtx(transaction)

        if self.verbose:
            print("got", txid)

        try:
            result = self.pusher.push_tx(self.destination, raw_tx)
            ret = ['success', result]
        except Exception as exc:
            ret = ['failure', str(exc)]

        if self.verbose:
            print("Result of push:", ret[0], ret[1])

        return ret

    def replay_mempool(self):
        watch_mempool(self.source, self._replay_tx)
