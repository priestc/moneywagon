from __future__ import print_function

import math
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

def find_index_fast(target, sorted_base16, length, start_length=4, verbose=False):
    start_length += 3
    target_value = int(target[:start_length], 16)
    index_guess = int(round(target_value / float(16 ** start_length) * length))
    finds = []

    while True:
        if index_guess + 1 >= length:
            found = sorted_base16[-1]
        else:
            found = sorted_base16[index_guess]

        if verbose: print("iterating:", index_guess)

        if index_guess in finds:
            # oscilation discovered, iterate between osciliation points
            prev = finds[-1]
            avg = int((prev + index_guess) / 2)
            j = 0
            while True:
                if avg + j < length:
                    if target == sorted_base16[avg + j]:
                        ret = avg + j
                        break
                if avg - j > 0:
                    if target == sorted_base16[avg - j]:
                        ret = avg - j
                        break
                j += 1
            if verbose: print(
                "found", found[:start_length], "after", len(finds), "iterations",
                "and", j, "oscilation iterations."
            )
            return ret

        finds.append(index_guess)

        if found == target:
            if verbose: print("found", found[:start_length], "after", len(finds), "iterations")
            return index_guess
        found_value = int(found[:start_length] or ('f' * start_length), 16)
        found_percentage = found_value / float(16**(start_length))
        off_by = found_value - target_value
        off_by_percentage = off_by / float(16 ** start_length)

        if off_by < 0:
            adjust_by = int(math.floor(off_by_percentage * length))
        else:
            adjust_by = int(math.ceil(off_by_percentage * length))
        index_guess = index_guess - adjust_by

        if index_guess < 0:
            index_guess = 0
        if index_guess > length:
            index_guess = length

index_timer = 0
def get_unique(txid, sorted_mempool, start_length, mempool_length, extra_bytes=1):
    global index_timer
    t0 = datetime.datetime.now()
    index = find_index_fast(txid, sorted_mempool, mempool_length, start_length)
    index_timer += (datetime.datetime.now() - t0).total_seconds()

    if index == 0:
        before = ''
    else:
        before = sorted_mempool[index-1]

    if index + 1 >= mempool_length:
        after = ''
    else:
        after = sorted_mempool[index+1]

    i = start_length
    while txid[:i] in (before[:i], after[:i]):
        if i > 8:
            print(
                index, mempool_length, "txid", txid[:i], "before",
                before[:i], "after", after[:i]
            )
        i += 1
        if i > 30:
            raise SystemExit()

    return txid[:i+extra_bytes]

def encode_mempool(mempool, extra_bytes=2, verbose=False):
    mempool_length = len(mempool)

    t1 = datetime.datetime.now()
    sorted_mempool = sorted(mempool)
    sorting_time = datetime.datetime.now() - t1

    start_length = get_start_length(mempool_length)

    short_ids = []
    t2 = datetime.datetime.now()
    for tx in mempool:
        short_ids.append(
            get_unique(
                tx, sorted_mempool,
                start_length=start_length, mempool_length=mempool_length,
                extra_bytes=extra_bytes
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

def get_full_id(short_id, sorted_base16, length):

    def extended_find(found_index, positive=False, negative=False):
        j = 0
        matches = []
        while True:
            if positive and found_index + j <= (length - 1):
                try_ = found_index + j
            elif negative and found_index - j > 0:
                try_ = found_index - j
            else:
                return matches # no additional matches found

            try:
                next = sorted_base16[try_]
            except:
                import ipdb; ipdb.set_trace()

            if not next.startswith(short_id):
                return matches
            matches.append(next)
            j += 1

    i = 0
    skip = calculate_skip(short_id, 3, length)
    while True:
        p_try = skip + i
        if p_try < length and sorted_base16[p_try].startswith(short_id):
            return extended_find(p_try, positive=True)

        n_try = skip - i
        if n_try > 0 and sorted_base16[n_try].startswith(short_id):
            return extended_find(n_try, negative=True)
        i += 1
        if i >= length:
            return None # no match found

def decode_superthin_chunk(short_ids, sorted_mempool, length, verbose=False):
    full_ids = []
    duplicates = []
    missing = []
    for short_id in short_ids:
        found = get_full_id(short_id, sorted_mempool, length)
        if not found:
            if verbose: print("missing:", short_id)
            full_ids.append(short_id)
            missing.append(short_id)
        elif len(found) > 1:
            if verbose:
                print("found duplicates of %s: %s" % (
                    short_id, ', '.join("%s..." % x[:10] for x in found)
                ))
            full_ids.append("dupe")
            duplicates.append(found)
        else:
            full_ids.append(found[0])

    return full_ids, missing, duplicates

def prod(iterable):
    p = 1
    for n in iterable:
        p *= n
    return p

def all_combinations(duplicates, i=0):
    if i >= prod(len(x) for x in duplicates):
        return None # all combinations have been tried
    this_pass = []
    for item in duplicates:
        l = len(item)
        this_i = i % l
        i = int(i / l)
        this_pass.append(item[this_i])

    return this_pass

def decode_superthin(short_ids, mempool, hash, threads=4, verbose=False):
    smp = sorted(mempool)
    length = len(mempool)
    full_ids, missing, duplicates = decode_superthin_chunk(
        short_ids, smp, length, verbose=verbose
    )

    if missing:
        if verbose:
            print("Missing:\n%s...\n" % x[:10] for x in missing)
            return # todo: fetch misssing
    elif verbose:
        print("No missing txids!")

    if duplicates:
        i = 0
        while True:
            group = all_combinations(duplicates, i)
            if not group:
                if verbose: print("Tried all duplicate groups: decode failed")
                return None # decode failed
            if verbose: print("Trying duplicate group %s, %s" % (i, str(group)))
            this_try = []
            hash_try = sha256()
            for txid in full_ids:
                if txid == 'dupe':
                    try_ = group.pop()
                    this_try.append(try_)
                    hash_try.update(try_)
                else:
                    this_try.append(txid)
                    hash_try.update(txid)

            if hash_try.hexdigest() == hash:
                if verbose: print("Group %s suceeded!" % i)
                return full_ids
            i += 1

    elif verbose:
        print("Found no duplicates!")

    decoded_hash = sha256(''.join(full_ids)).hexdigest()
    if decoded_hash == hash:
        if verbose: print("Hash succeeded!")
        return full_ids
    else:
        if verbose: print("Hash failed?")
        return None



if __name__ == '__main__':
    def modify_mempool(mempool, remove=10, add=10, verbose=False):
        """
        Given a list of txids (mempool), add and remove some items to simulate
        an out of sync mempool.
        """
        random.shuffle(mempool)
        for i in range(add):
            new_txid = _make_txid()
            mempool.append(new_txid)
            if verbose: print("added:", new_txid)

        for i in range(remove):
            popped = mempool.pop()
            if verbose: print("removed:", popped)

        return mempool

    def compare_index_finders():
        mp = make_mempool(mb=32)
        l = len(mp)
        smp = sorted(mp)
        t0 = datetime.datetime.now()
        for i, txid in enumerate(mp):
            find_index_fast(txid, smp, l, start_length=4)
            #print("%.4f%%" % (i / float(l)))
        print("optimized", datetime.datetime.now() - t0)

        t0 = datetime.datetime.now()
        for i, txid in enumerate(mp):
            smp.index(txid)
        print("un-optimized", datetime.datetime.now() - t0)

    def _get_mempool_from_file():
        t0 = datetime.datetime.now()
        with open('mp.txt') as f:
            mp = [x.strip() for x in f.readlines()]
        print("loaded mempool from file, took: %s" % (
            datetime.datetime.now() - t0
        ))
        return mp

    def test_from_file(index=None, key=None):
        smp = _get_mempool_from_file()
        if not index and not key:
            for i, txid in enumerate(smp):
                index = find_index_fast(txid, smp, len(smp))
                if i != index:
                    print(i, index)
        elif index:
            result = find_index_fast(smp[index], smp, len(smp))
            print(index, result)
        elif key:
            result = find_index_fast(key, smp, len(smp))
            print(index, result)

    def test_file_encodde():
        mp = _get_mempool_from_file()
        random.shuffle(mp)
        encoded, hash = encode_mempool(mp, verbose=True)

    def performance_test_encode():
        # testing encoding of large mempools
        for size in [32, 64, 128, 256]:
            mp = make_mempool(mb=size, verbose=True)
            encoded, hash = encode_mempool(mp, verbose=True)
            print("-----")

    def test_not_completely_synced(from_file=False):
        """
        tesing decoding against not completely synced mempools
        """
        if not from_file:
            mp = make_mempool(mb=8, verbose=False)
        else:
            mp = _get_mempool_from_file()
        t0 = datetime.datetime.now()
        encoded, hash = encode_mempool(mp, verbose=False)
        encoding_time = datetime.datetime.now() - t0
        print("encoding complete, took: %s" % encoding_time)

        for action in [{'add': 1000}]:
            modified_mempool = modify_mempool(mp, **action)
            t1 = datetime.datetime.now()
            full_ids = decode_superthin(
                encoded, modified_mempool, hash=hash, verbose=True
            )
            decoding_time = datetime.datetime.now() - t1
            print("decoding took: %s" % decoding_time)

    test_not_completely_synced(from_file=True)
