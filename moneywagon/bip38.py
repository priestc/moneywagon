from __future__ import print_function

from binascii import unhexlify, hexlify
from hashlib import sha256
from unicodedata import normalize
import sys

from moneywagon.core import get_magic_bytes
from bitcoin import (
    privtopub, pubtoaddr, encode_privkey, get_privkey_format,
    encode_pubkey, changebase, fast_multiply, G
)

try:
    import scrypt
except ImportError:
    raise ImportError("Scrypt is required for BIP38 support: pip install scrypt")

try:
    from Crypto.Cipher import AES
except ImportError:
    raise ImportError("Pycrypto is required for bip38 support: pip install pycrypto")

is_py2 = False
if sys.version_info <= (3,0):
    # py2
    is_py2 = True
else:
    # py3
    long = int
    unicode = str

def base58check(payload):
    checksum = sha256(sha256(payload).digest()).digest()[:4] # b58check for encrypted privkey
    return changebase(hexlify(payload + checksum).decode('ascii'), 16, 58)


def bip38_encrypt(crypto, privkey, passphrase):
    """
    BIP0038 non-ec-multiply encryption. Returns BIP0038 encrypted privkey.
    """
    pub_byte, priv_byte = get_magic_bytes(crypto)
    privformat = get_privkey_format(privkey)
    if privformat in ['wif_compressed','hex_compressed']:
        compressed = True
        flagbyte = b'\xe0'
        if privformat == 'wif_compressed':
            privkey = encode_privkey(privkey,'hex_compressed')
            privformat = get_privkey_format(privkey)
    if privformat in ['wif', 'hex']:
        compressed = False
        flagbyte = b'\xc0'
    if privformat == 'wif':
        privkey = encode_privkey(privkey,'hex')
        privformat = get_privkey_format(privkey)

    pubkey = privtopub(privkey)
    addr = pubtoaddr(pubkey, pub_byte)

    passphrase = normalize('NFC', unicode(passphrase))
    if is_py2:
        ascii_key = addr
        passphrase = passphrase.encode('utf8')
    else:
        ascii_key = bytes(addr,'ascii')

    salt = sha256(sha256(ascii_key).digest()).digest()[0:4]
    key = scrypt.hash(passphrase, salt, 16384, 8, 8)
    derivedhalf1, derivedhalf2 = key[:32], key[32:]

    aes = AES.new(derivedhalf2)
    encryptedhalf1 = aes.encrypt(unhexlify('%0.32x' % (long(privkey[0:32], 16) ^ long(hexlify(derivedhalf1[0:16]), 16))))
    encryptedhalf2 = aes.encrypt(unhexlify('%0.32x' % (long(privkey[32:64], 16) ^ long(hexlify(derivedhalf1[16:32]), 16))))

    payload = b'\x01\x42' + flagbyte + salt + encryptedhalf1 + encryptedhalf2
    return base58check(payload)


def bip38_decrypt(crypto, encrypted_privkey, passphrase, wif=False):
    """
    BIP0038 non-ec-multiply decryption. Returns hex privkey.
    """
    pub_byte, priv_byte = get_magic_bytes(crypto)
    passphrase = normalize('NFC', unicode(passphrase))
    if is_py2:
        passphrase = passphrase.encode('utf8')

    d = unhexlify(changebase(encrypted_privkey, 58, 16, 86))

    # trim off first 2 bytes (0x01c) (\x01\x42)
    d = d[2:]
    flagbyte = d[0:1]
    d = d[1:]
    # respect flagbyte, return correct pair

    if flagbyte == b'\xc0':
        compressed = False
    if flagbyte == b'\xe0':
        compressed = True
    else:
        raise Exception("Only non-ec mode at this time.")

    addresshash = d[0:4]
    d = d[4:-4]
    key = scrypt.hash(passphrase,addresshash, 16384, 8, 8)
    derivedhalf1 = key[0:32]
    derivedhalf2 = key[32:64]
    encryptedhalf1 = d[0:16]
    encryptedhalf2 = d[16:32]
    aes = AES.new(derivedhalf2)
    decryptedhalf2 = aes.decrypt(encryptedhalf2)
    decryptedhalf1 = aes.decrypt(encryptedhalf1)
    priv = decryptedhalf1 + decryptedhalf2
    priv = unhexlify('%064x' % (long(hexlify(priv), 16) ^ long(hexlify(derivedhalf1), 16)))
    pub = privtopub(priv)
    if compressed:
        pub = encode_pubkey(pub,'hex_compressed')
    addr = pubtoaddr(pub, pub_byte)

    if is_py2:
        ascii_key = addr
    else:
        ascii_key = bytes(addr,'ascii')

    if sha256(sha256(ascii_key).digest()).digest()[0:4] != addresshash:
        raise Exception('Bip38 password decrypt failed: Wrong password?')
    else:
        formatt = 'wif' if wif else 'hex'
        if compressed:
            return encode_privkey(priv, formatt + '_compressed')
        else:
            return encode_privkey(priv, formatt)

def compress(x, y):
    """
    Given a x,y coordinate, encode in "compressed format"
    """
    polarity = "02" if y % 2 == 0 else "03"
    return "%s%x" % (polarity, x)

def bip38_generate_intermediate_point(passphrase, seed, lot=None, sequence=None):
    passphrase = normalize('NFC', unicode(passphrase))
    if is_py2:
        passphrase = passphrase.encode('utf8')

    if not is_py2:
        seed = bytes(seed, 'ascii')

    if lot and sequence:
        ownersalt = sha256(seed).digest()[:4]
        lotseq = unhexlify("%0.8x" % (4096 * lot + sequence))
        #print("lotseq:", lotseq, len(lotseq))
        ownerentropy = ownersalt + lotseq
    else:
        ownersalt = ownerentropy = sha256(seed).digest()[:8]

    #print("ownersalt:", ownersalt, len(ownersalt))
    #print("ownerentropy:", ownerentropy, len(ownerentropy))

    prefactor = scrypt.hash(passphrase, ownersalt, 16384, 8, 8, 32)

    if lot and sequence:
        passfactor = sha256(sha256(prefactor + ownerentropy).digest()).digest()
    else:
        passfactor = prefactor

    #print("passfactor:", passfactor, len(passfactor))

    if is_py2:
        as_int = int(prefactor.encode('hex'), 16)
    else:
        as_int = int.from_bytes(prefactor, byteorder='big')

    ppx, ppy = fast_multiply(G, as_int)
    passpoint = compress(ppx, ppy)

    if not is_py2:
        passpoint = bytes(passpoint, 'ascii')

    passpoint = unhexlify(passpoint)

    #print("passpoint", passpoint, len(passpoint))

    last_byte = b'\x53' if not lot and not sequence else b'\x52'
    magic_bytes = b'\x2C\xE9\xB3\xE1\xFF\x39\xE2' + last_byte # 'passphrase' prefix
    payload = magic_bytes + ownerentropy + passpoint

    #print("payload:", len(payload))

    return base58check(payload)


def test():
    # taken directly from the BIP38 whitepaper
    cases = [[
        'btc',
        '6PRVWUbkzzsbcVac2qwfssoUJAN1Xhrg6bNk8J7Nzm5H7kxEbn2Nh2ZoGg',
        'cbf4b9f70470856bb4f40f80b87edb90865997ffee6df315ab166d713af433a5',
        u'TestingOneTwoThree',
        False
        ], [
        'btc',
        '6PRNFFkZc2NZ6dJqFfhRoFNMR9Lnyj7dYGrzdgXXVMXcxoKTePPX1dWByq',
        '09c2686880095b1a4c249ee3ac4eea8a014f11e6f986d0b5025ac1f39afbd9ae',
        u'Satoshi',
        False
        ],[
        'btc',
        '6PRW5o9FLp4gJDDVqJQKJFTpMvdsSGJxMYHtHaQBF3ooa8mwD69bapcDQn',
        '5Jajm8eQ22H3pGWLEVCXyvND8dQZhiQhoLJNKjYXk9roUFTMSZ4',
        u'\u03D2\u0301\u0000\U00010400\U0001F4A9',
        True,
        ],[
        'btc',
        '6PYNKZ1EAgYgmQfmNVamxyXVWHzK5s6DGhwP4J5o44cvXdoY7sRzhtpUeo',
        'L44B5gGEpqEDRS9vVPz7QT35jcBG2r3CZwSwQ4fCewXAhAhqGVpP',
        u'TestingOneTwoThree',
        True
        ],[
        'btc',
        '6PYLtMnXvfG3oJde97zRyLYFZCYizPU5T3LwgdYJz1fRhh16bU7u6PPmY7',
        'KwYgW8gcxj1JWJXhPSu4Fqwzfhp5Yfi42mdYmMa4XqK7NJxXUSK7',
        u'Satoshi',
        True
        ],[
        'ltc',
        '6PfQ31ycwn3HALREcJvKz9xUDoEstPX9KqYuaFXBfc7Qnk6WSgP7xnXmB1',
        'not yet',
        'arise',
        False
    ]]

    index = 1
    for crypto, encrypted_key, unencrypted_key, password, use_wif in cases:
        test_encrypted = bip38_encrypt(crypto, unencrypted_key, password)
        test_decrypted = bip38_decrypt(crypto, encrypted_key, password, wif=use_wif)
        assert encrypted_key == test_encrypted, "encrypt failed"
        assert unencrypted_key == test_decrypted, 'decrypt failed'
        print("Test #%s passed" % index)
        index += 1
