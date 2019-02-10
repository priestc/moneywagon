from __future__ import print_function

import binascii
import datetime
from base58 import b58encode, b58decode
from bitcoin import sha256, pubtoaddr, privtopub, bin_hash160
import requests

from moneywagon.crypto_data import crypto_data
from moneywagon import change_version_byte, is_py2, CurrencyNotSupported
from moneywagon.crypto_data_extractor import crawl_SLIP44

def nthprime(n):
    if n==0:
        return 2
    if n == 1:
        return 3

    n = n + 1

    count = 1
    num = 3
    while(count <= n):
        if is_prime(num):
            count +=1
            if count == n:
               return num
        num +=2 #optimization

def is_prime(num):
    factor = 2
    while (factor < num):
        if num%factor == 0:
             return False
        factor +=1
    return True

def gen_primes():
    """ Generate an infinite sequence of prime numbers.
    """
    D = {}
    q = 2
    while True:
        if q not in D:
            yield q
            D[q * q] = [q]
        else:
            for p in D[q]:
                D.setdefault(p + q, []).append(p)
            del D[q]

        q += 1

def py2_from_bytes(data, big_endian = False):
    if isinstance(data, str):
        data = bytearray(data)
    if big_endian:
        data = reversed(data)
    num = 0
    for offset, byte in enumerate(data):
        num += byte << (offset * 8)
    return num

def to_bytes(number):
    try:
        # Python 3
        return number.to_bytes((number.bit_length() + 7) // 8, 'little')
    except AttributeError:
        # Python 2
        h = '%x' % number
        s = ('0'*(len(h) % 2) + h).zfill(2).decode('hex')
        return s[::-1]

def to_number(bytez):
    try:
        # python 3
        return int.from_bytes(bytez, 'little')
    except AttributeError:
        # python 2
        return py2_from_bytes(bytez)

def get_currency_by_order(order):
    #print("getting currency for order: %s" % order)
    bip44 = order + 0x80000000
    for currency, data in crypto_data.items():
        if data['bip44_coin_type'] == bip44:
            #print("found %s" % currency)
            return currency
    try:
        #print("not a moneywagon currency, crawling slip44")
        coins = crawl_SLIP44()
        for currency, data in coins.items():
            if data[0] == order:
                #print("found %s at order %s" % (currency, order))
                return currency
    except:
        pass

    raise CurrencyNotSupported("Currency order %s not found" % order)

def get_slip44_index(currency):
    #print("getting index for %s" % currency)
    try:
        curr = crypto_data[currency.lower()]
        index = curr['bip44_coin_type'] - 0x80000000
        #print("index is %s (from moneywagon)" % index)
        return index
    except (KeyError, CurrencyNotSupported):
        #print("not a moneywagon currency, crawling slip44")
        coins = crawl_SLIP44()
        index = coins[currency.lower()][0]
        #print("index is %s (from slip44)" % index)
        return index

    raise CurrencyNotSupported("Unknown currency: %s" % currency)


def encode_currency_support_token(currency_list):
    token = 1
    for currency in currency_list:
        index = get_slip44_index(currency)
        t0 = datetime.datetime.now()
        nth = nthprime(index)
        token *= nth
        print("found", index, "th prime: ", nth)
        print("took", datetime.datetime.now() - t0)

    return b58encode(to_bytes(token))

def largest_prime_factor(n):
    i = 2
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
    return n

def decode_currency_support_token(token):
    token = to_number(b58decode(token))
    currencies = []

    print("factoring %s" % token)
    t0 = datetime.datetime.now()
    if is_py2:
        import primefac
        factors = sorted(list(primefac.primefac(token)))
    else:
        factors = find_factors()

    print("factors are %s" % factors)
    print("factoring took %s" % (datetime.datetime.now() - t0))

    for order, p in enumerate(gen_primes()):
        if p in factors:
            currencies.append(get_currency_by_order(order))
            if len(factors) == len(currencies):
                break

    return sorted(currencies)

def generate_mcaf(currencies, seed, mode="P"):
    priv = sha256(seed)
    pub = privtopub(priv)
    #import ipdb; ipdb.set_trace()
    hash160 = binascii.hexlify(bin_hash160(binascii.unhexlify(pub)))

    print(hash160, b58encode(hash160))

    if mode == 'P':
        address = "P%s0%s" % (
            encode_currency_support_token(currencies).decode("utf-8"),
            b58encode(hash160).decode("utf-8")
        )
    else:
        raise NotImplementedError("Only P mode implemented")

    return "%s%s" % (address, sha256(address)[:4])

def decode_mcaf(address):
    if not address.startswith("P"):
        raise NotImplementedError("Only P mode implemented at this time")

    address = address.replace("O", "0")

    if not sha256(address[:-4]) == address[-4:]:
        raise Exception("Invalid checksum")

    token, payload = address.split("0")
    currencies = decode_currency_support_token(token[1:])
    ret = {}
    for currency in currencies:
        try:
            ret[currency] = change_version_byte(
                payload, to_crypto=currency
            )
        except CurrencyNotSupported as exc:
            ret[currency] = str(exc)

    return ret

def encode_binary(indexes):
    total = 0
    for index in indexes:
        total += pow(2, index)
    return total

def decode_binary(indexes):
    pass

if __name__ == "__main__":

    #print(encode_binary([1, 5, 6]))
    #print(encode_binary([5, 6, 57352]))

    cases = [
        #['ltc', 'btc', 'zec', 'doge', 'eth', 'bch', 'uno'],
        #['ltc', 'btc'],
        #['btc', 'bch'],
        ['dash', 'eth', 'vtc', 'btv']
    ]
    for i, case in enumerate(cases):
        case = sorted(case)
        encoded = encode_currency_support_token(case)
        result = sorted(decode_currency_support_token(encoded))

        print("Case %s" % i, end=' ')
        if result == case:
            print("Passed", result, str(encoded))
        else:
            print("Failed. Decode returned %s expected %s" % (result, case))

        print("--------")
