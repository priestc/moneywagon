from __future__ import print_function

import datetime
from hashlib import sha256
import random

def _make_txid():
    return sha256(str(random.random())).hexdigest()

def make_mempool(mb=8, kb=None, verbose=False):
    if verbose:
        t0 = datetime.datetime.now()

    if kb:
        n = int(kb * 1024.0 / 266)
    else:
        n = int(mb * 1024.0 * 1024.0 / 266)

    mempool = []
    for i in xrange(n):
        mempool.append(_make_txid())

    if verbose:
        print("generated %s %s mempool with %s transactions, took: %s" % (
            kb or mb,
            'KB' if kb else 'MB',
            len(mempool),
            datetime.datetime.now() - t0
        ))
    return mempool

def get_start_length(size):
    start_length = 1
    while True:
        if float(size) / (16 ** (start_length)) < 1:
            return start_length
        else:
            start_length += 1

def calculate_skip(target, start_length, length):
    return int(
        int(target[:start_length], 16) / float(16 ** start_length) * length
    )

def find_index_fast(target, sorted_base16, length, start_length):
    skip = calculate_skip(target, start_length, length)
    i = 0
    while True:
        try:
            if sorted_base16[skip + i] == target:
                return skip + i
        except IndexError:
            pass
        try:
            if sorted_base16[skip - i] == target:
                return skip - i
        except IndexError:
            pass
        i += 1

index_timer = 0
def get_unique(txid, sorted_mempool, start_length, mempool_length):
    global index_timer
    t0 = datetime.datetime.now()
    #index = sorted_mempool.index(txid)
    index = find_index_fast(txid, sorted_mempool, mempool_length, start_length)
    index_timer += (datetime.datetime.now() - t0).total_seconds()

    if index == 0:
        before = ''
    else:
        before = sorted_mempool[index-1]

    after = sorted_mempool[index+1]
    unique_prefix = txid[:start_length]
    to_iterate = txid[start_length:]

    if before[:start_length] != unique_prefix and unique_prefix != after[:start_length]:
        return unique_prefix

    unique = ''
    for i, char in enumerate(to_iterate):
        unique += char
        before_unique = not before[start_length:].startswith(unique)
        after_unique = not after[start_length:].startswith(unique)
        if before_unique and after_unique:
            return unique_prefix + unique

    return unique_prefix + unique

def encode_mempool(mempool, verbose=False):
    mempool_length = len(mempool)

    t1 = datetime.datetime.now()
    sorted_mempool = sorted(mempool) + ['']
    sorting_time = datetime.datetime.now() - t1

    start_length = get_start_length(mempool_length)

    short_ids = []
    t2 = datetime.datetime.now()
    for tx in mempool:
        short_ids.append(
            get_unique(
                tx, sorted_mempool,
                start_length=start_length, mempool_length=mempool_length
            )
        )
    encoding_time = datetime.datetime.now() - t2

    t3 = datetime.datetime.now()
    hash = sha256(''.join(x for x in mempool)).hexdigest()
    hash_time = datetime.datetime.now() - t3

    if verbose:
        print("encoding mempool took: %s" % encoding_time)
        print("sorting mempool took: %s" % sorting_time)
        print("using start length of: %s" % start_length)

        size = sum(len(x) for x in short_ids)
        avg_bytes_per_tx = size / float(mempool_length)
        print("average bytes per tx: %.4f" % avg_bytes_per_tx)

        total_weight = (size + mempool_length) / 1048576.0 # 1024 ** 2
        print("total weight: %.2f MB" % total_weight)

        mempool_size = ((mempool_length * 266.0) / 1048576)
        print(
            "compression percentage: %.2f%%" % (
                100 - (100.0 * (total_weight / mempool_size))
            )
        )

        print("encoding speed: %.2f tps" % (
            float(mempool_length) / encoding_time.total_seconds()
        ))
        #print("length of set: %s" % len(set(short_ids)))
        print("unique encoding?: %s" % (len(set(mempool)) == mempool_length))

        global index_timer
        print("seconds spent finding index: %.2f (%.2f%%)" % (index_timer, (100.0 * index_timer/encoding_time.total_seconds() )))
        index_timer = 0

        print("time to make hash: %s" % hash_time)

    return short_ids, hash

def decode_superthin(short_ids, mempool, hash, verbose=False):
    pass

def test_find_fast_index(index):
    sl = get_start_length(len(mp))
    return find_index_fast(s[index], s, len(s), sl)

def mame_mempool(mempool, by=10, verbose=False):
    random.shuffle(mempool)
    for i in range(by):
        popped = mempool.pop()
        new_txid = _make_txid()
        mempool.append(new_txid)
        if verbose:
            print("removed:", popped)
            print("added:", new_txid)

if __name__ == '__main__':
    # testing encoding of large mempools
    for size in [32]: #, 64, 128]:
        print("-----")
        mp = make_mempool(mb=size, verbose=True)
        encoded, hash = encode_mempool(mp, verbose=True)

    print("---------")

    # tesing decoding against not completely synced mempools
    mp = make_mempool(mb=8, verbose=False)
    t0 = datetime.datetime.now()
    encoded, hash = encode_mempool(mp, verbose=False)
    encoding_time = datetime.datetime.now() - t0
    for mame in [10, 20, 30, 40]:
        mamed = mame_mempool(mp, by=mame)
        t1 = datetime.datetime.now()
        decode_superthin(encoded, mamed, hash=hash, verbose=True)
        decoding_time = datetime.datetime.now() - t1
