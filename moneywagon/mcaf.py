from __future__ import print_function
from base58 import b58encode, b58decode
import primefac

from moneywagon.crypto_data import crypto_data
from moneywagon import change_version_byte

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
    bip44 = order + 0x80000000
    for currency, data in crypto_data.items():
        if data['bip44_coin_type'] == bip44:
            return currency
    raise Exception("Currency order %s not found" % order)

def get_currency_order(currency):
    try:
        curr = crypto_data[currency]
    except KeyError:
        raise Exception("%s Not Supported" % currency)
    return curr['bip44_coin_type'] - 0x80000000

def encode(currency_list):
    token = 1
    for currency in currency_list:
        order = get_currency_order(currency)
        #print "adding:", currency, "order:", order, "prime:", primes[order]
        token *= nthprime(order)
    #print "final product:", token
    return b58encode(to_bytes(token))

def largest_prime_factor(n):
    i = 2
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
    return n

def decode(token):
    token = to_number(b58decode(token))
    currencies = []
    factors = sorted(list(primefac.primefac(token)))

    for order, p in enumerate(gen_primes()):
        if p in factors:
            currencies.append(get_currency_by_order(order))
            if len(factors) == len(currencies):
                break

    return sorted(currencies)

def make_mcaf(currencies, address, mode="P"):
    if mode == 'P':
        return "P%s0%s" % (encode(currencies), address)
    else:
        raise NotImplementedError()

def decode_mcaf(address, mode="P"):
    address = address.replace("O", "0")
    token, payload = address.split("0")
    currencies = decode(token[1:])
    ret = {}
    for currency in currencies:
        new_version = crypto_data[currency].get('address_version_byte', None)
        ret[currency] = change_version_byte(
            payload, new_version
        ) if new_version else None

    return ret


if __name__ == "__main__":
    cases = [
        ['ltc', 'btc', 'zec', 'doge', 'eth', 'bch', 'uno'],
        ['ltc', 'btc'],
        ['btc', 'bch'],
        ['dash', 'eth', 'vtc']
    ]
    for i, case in enumerate(cases):
        case = sorted(case)
        encoded = encode(case)
        result = sorted(decode(encoded))
        print("Case %s" % i, end=' ')
        if result == case:
            print("Passed", result, str(encoded))
        else:
            print("Failed. Decode returned %s expected %s" % (result, case))

        print("--------")
