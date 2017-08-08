from __future__ import print_function

import random
from crypto_data import crypto_data
from moneywagon import get_block, push_tx, get_single_transaction
from .core import to_rawtx
from moneywagon.services import BitpayInsight, ChainSo, LocalBitcoinsChain, BlockDozer

def replay_block(source, destination, block_to_replay, verbose=False, block_fetcher=None, limit=5):
    """
    Replay all transactions in parent currency to passed in "source" currency,
    and vice versa. Block_to_replay can either be an integer or a block object.
    `block_fetcher` is a callable that will return a block.
    """
    parent_currency, parent_fork_block = crypto_data[source.lower()].get('forked_from') or [None, 0]
    child_currency, child_fork_block = crypto_data[destination.lower()].get('forked_from') or [None, 0]

    if not parent_currency and not child_currency:
        raise Exception("Networks %s and %s are not forks of one another." % (
            source.upper(), destination.upper()
        ))

    if block_to_replay == 'latest':
        if verbose:
            print("Getting latest %s block" % source.upper())
        block = get_block(source, latest=True, verbose=verbose)
        if verbose:
            print("Latest %s block is #%s" % (source.upper(), block['block_number']))
    elif type(block_to_replay) is not dict:
        if verbose:
            print("Getting %s block #%s" % (source.upper(), block_to_replay))
        block = get_block(source, block_number=int(block_to_replay), verbose=verbose)
    else:
        block = block_to_replay

    bn = block['block_number']
    if bn < parent_fork_block or bn < child_fork_block:
        raise Exception("Can't replay blocks mined before the fork")

    if source.lower() == 'btc':
        pusher = BlockDozer(verbose=verbose)
        service = random.choice([BitpayInsight, ChainSo, LocalBitcoinsChain])(verbose=verbose)
    elif source.lower() == 'bch':
        pusher = random.choice(crypto_data['btc']['services']['push_tx'])(verbose=verbose)
        service = BlockDozer(verbose=verbose)
    else:
        raise Exception("Only BTC and BCH are currently supported")

    if verbose:
        print("Using %s for pushing to %s" % (pusher.name, destination.upper()))
        print("Using %s for getting %s transactions" % (service.name, source.upper()))
        print("Finished getting block header,", len(block['txids']), "transactions in block, will replay", (limit or "all of them"))

    results = []
    enforced_limit = (limit or len(block['txids']))

    for i, txid in enumerate(block['txids'][:enforced_limit]):
        if block_fetcher:
            transaction = block_fetcher(currency=source, txid=txid)
        else:
            transaction = service.get_single_transaction(source, txid=txid)

        first_input = transaction['inputs'][0]
        if first_input.get('coinbase') or first_input.get("addresses") == "coinbase":
            continue # no point trying to replay coinbases.

        raw_tx = to_rawtx(transaction)

        if verbose:
            print("got tx", i, "of", len(block['txids']))

        try:
            result = pusher.push_tx(destination, raw_tx)
            ret = ['success', result]
        except Exception as exc:
            ret = ['failure', str(exc)]

        if verbose:
            print("Result of push:", ret[0], ret[1])

        yield ret
