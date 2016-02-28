# -*- coding: utf-8 -*-
from __future__ import print_function

from binascii import unhexlify, hexlify
from hashlib import sha256
from unicodedata import normalize
import sys

from moneywagon.core import get_magic_bytes
from bitcoin import (
    privtopub, pubtoaddr, encode_privkey, get_privkey_format,
    encode_pubkey, changebase, fast_multiply, G, P, A, B
)

from base58 import b58encode_check, b58decode_check

try:
    import scrypt
except ImportError:
    raise ImportError("Scrypt is required for BIP38 support: pip install scrypt")

try:
    from Crypto.Cipher import AES
except ImportError:
    raise ImportError("PyCrypto is required for bip38 support: pip install pycrypto")

is_py2 = False
if sys.version_info <= (3,0):
    # py2
    is_py2 = True
else:
    # py3
    long = int
    unicode = str

def compress(x, y):
    """
    Given a x,y coordinate, encode in "compressed format"
    Returned is always 33 bytes.
    """
    polarity = "02" if y % 2 == 0 else "03"

    wrap = lambda x: x
    if not is_py2:
        wrap = lambda x: bytes(x, 'ascii')

    return unhexlify(wrap("%s%0.64x" % (polarity, x)))


def uncompress(payload):
    """
    Given a compressed ec key in bytes, uncompress it using math and return (x, y)
    """
    payload = hexlify(payload)
    even = payload[:2] == b"02"
    x = int(payload[2:], 16)
    beta = pow(int(x ** 3 + A * x + B), int((P + 1) // 4), int(P))
    y = (P-beta) if even else beta
    return x, y

def bytes_to_int(x):
    if is_py2:
        return int(x.encode('hex'), 16)
    else:
        return int.from_bytes(x, byteorder='big')


class Bip38Primitive(object):
    def __str__(self):
        return self.b58check


class Bip38EncryptedPrivateKey(Bip38Primitive):

    def __init__(self, crypto, b58check):
        if not b58check.startswith('6P'):
            raise Exception("Invalid encrypted private key. Must start wth 6P.")
        self.b58check = b58check
        self.payload = b58decode_check(b58check)
        second_byte = self.payload[1:2]
        self.flagbyte = self.payload[2:3]

        if second_byte == b'\x42':
            self.ec_multiply = False
            if self.flagbyte == b'\xC0':
                self.compressed = False
            elif self.flagbyte == b'\xE0':
                self.compressed = True
            else:
                raise Exception("Unknown flagbyte: %x" % flagbyte)

            self.addresshash = self.payload[3:7] # 4 bytes
            self.encryptedhalf1 = self.payload[7:23] # 16 bytes
            self.encryptedhalf2 = self.payload[23:39] # 16 bytes

        elif second_byte == b'\x43':
            self.ec_multiply = True
            if self.flagbyte == b'\x00':
                self.compressed = False
            elif self.flagbyte == b'\x20':
                self.compressed = True
            else:
                raise Exception("Unknown flagbyte: %x" % flagbyte)

            self.addresshash = self.payload[3:7] # 4 bytes
            self.ownerentropy = self.payload[7:15] # 8 bytes
            self.encryptedpart1 = self.payload[15:23] # 8 bytes
            self.encryptedpart2 = self.payload[23:] # 16 bytes

        else:
            raise Exception("Unknown second base58check byte: %x" % second_byte)

        self.pub_byte, self.priv_byte = get_magic_bytes(crypto)

    def decrypt(self, passphrase, wif=False):
        """
        BIP0038 non-ec-multiply decryption. Returns hex privkey.
        """
        passphrase = normalize('NFC', unicode(passphrase))
        if is_py2:
            passphrase = passphrase.encode('utf8')

        if self.ec_multiply:
            raise Exception("Not supported yet")

        key = scrypt.hash(passphrase, self.addresshash, 16384, 8, 8)
        derivedhalf1 = key[0:32]
        derivedhalf2 = key[32:64]

        aes = AES.new(derivedhalf2)
        decryptedhalf2 = aes.decrypt(self.encryptedhalf2)
        decryptedhalf1 = aes.decrypt(self.encryptedhalf1)
        priv = decryptedhalf1 + decryptedhalf2
        priv = unhexlify('%064x' % (long(hexlify(priv), 16) ^ long(hexlify(derivedhalf1), 16)))
        pub = privtopub(priv)

        if self.compressed:
            pub = encode_pubkey(pub, 'hex_compressed')
        addr = pubtoaddr(pub, self.pub_byte)

        if is_py2:
            ascii_key = addr
        else:
            ascii_key = bytes(addr,'ascii')

        if sha256(sha256(ascii_key).digest()).digest()[0:4] != self.addresshash:
            raise Exception('Bip38 password decrypt failed: Wrong password?')
        else:
            formatt = 'wif' if wif else 'hex'
            if self.compressed:
                return encode_privkey(priv, formatt + '_compressed', self.priv_byte)
            else:
                return encode_privkey(priv, formatt, self.priv_byte)

    @classmethod
    def encrypt(cls, crypto, privkey, passphrase):
        """
        BIP0038 non-ec-multiply encryption. Returns BIP0038 encrypted privkey.
        """
        pub_byte, priv_byte = get_magic_bytes(crypto)
        privformat = get_privkey_format(privkey)
        if privformat in ['wif_compressed','hex_compressed']:
            compressed = True
            flagbyte = b'\xe0'
            if privformat == 'wif_compressed':
                privkey = encode_privkey(privkey, 'hex_compressed')
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

        # 39 bytes    2 (6P)      1(R/Y)    4          16               16
        payload = b'\x01\x42' + flagbyte + salt + encryptedhalf1 + encryptedhalf2
        return cls(crypto, b58encode_check(payload))

    @classmethod
    def create_from_intermediate(cls, crypto, intermediate_point, seed, compressed=True, include_cfrm=True):
        """
        Given an intermediate point, given to us by "owner", generate an address
        and encrypted private key that can be decoded by the passphrase used to generate
        the intermediate point.
        """
        flagbyte = b'\x20' if compressed else b'\x00'
        payload = b58decode_check(str(intermediate_point))
        ownerentropy = payload[8:16]

        passpoint = payload[16:-4]
        x, y = uncompress(passpoint)

        if not is_py2:
            seed = bytes(seed, 'ascii')

        seedb = hexlify(sha256(seed).digest())[:24]
        factorb = int(hexlify(sha256(sha256(seedb).digest()).digest()), 16)
        generatedaddress = pubtoaddr(fast_multiply((x, y), factorb))

        wrap = lambda x: x
        if not is_py2:
            wrap = lambda x: bytes(x, 'ascii')

        addresshash = sha256(sha256(wrap(generatedaddress)).digest()).digest()[:4]

        encrypted_seedb = scrypt.hash(passpoint, addresshash + ownerentropy, 1024, 1, 1, 64)
        derivedhalf1, derivedhalf2 = encrypted_seedb[:32], encrypted_seedb[32:]

        aes = AES.new(derivedhalf2)
        block1 = long(seedb[0:16], 16) ^ long(hexlify(derivedhalf1[0:16]), 16)
        encryptedpart1 = aes.encrypt(unhexlify('%0.32x' % block1))

        block2 = long(hexlify(encryptedpart1[8:16]) + seedb[16:24], 16) ^ long(hexlify(derivedhalf1[16:32]), 16)
        encryptedpart2 = aes.encrypt(unhexlify('%0.32x' % block2))

        # 39 bytes      2           1           4              8                8                 16
        payload = b"\x01\x43" + flagbyte + addresshash + ownerentropy + encryptedpart1[:8] + encryptedpart2
        encrypted_pk = b58encode_check(payload)

        if not include_cfrm:
            return generatedaddress, encrypted_pk

        confirmation_code = Bip38ConfirmationCode.create(flagbyte, ownerentropy, factorb, derivedhalf1, derivedhalf2, addresshash)
        return generatedaddress, cls(crypto, encrypted_pk), confirmation_code


class Bip38IntermediatePoint(Bip38Primitive):

    lotseq_constant = 4096

    def __init__(self, b58check):
        self.lot = None
        self.sequence = None
        self.b58check = b58check
        if not b58check.startswith('passphrase'):
            raise Exception("Invalid intermediate point. Must start wth 'passphrase'.")
        payload = b58decode_check(str(b58check))
        self.ownerentropy = payload[8:16] # 8 bytes
        self.passpoint = payload[16:49] # 33 bytes

        flag = payload[7:8]

        if flag == b'\x51':
            self.has_lot_and_sequence = True
            self.ownersalt = self.ownerentropy[:4] # 4 bytes
            lotsequence = bytes_to_int(self.ownerentropy[4:]) # 4 bytes
            self.lot = lotsequence // self.lotseq_constant
            self.sequence = lotsequence % self.lot
        elif flag == b'\x53':
            self.has_lot_and_sequence = False
            self.ownersalt = self.ownerentropy # 8 bytes
        else:
            raise Exception("Unknown flag byte: %s, should be either \\x51 or \\x53" % flag)

    @classmethod
    def create(cls, passphrase, seed=None, ownersalt=None, lot=None, sequence=None):
        passphrase = normalize('NFC', unicode(passphrase))
        if is_py2:
            passphrase = passphrase.encode('utf8')

        if seed and not is_py2:
            seed = bytes(seed, 'ascii')

        if ownersalt and len(ownersalt) != 8:
            raise Exception("Invalid salt")

        if lot and sequence:
            if not ownersalt:
                ownersalt = sha256(seed).digest()[:4]
            lotseq = unhexlify("%0.8x" % (self.lotseq_constant * lot + sequence))
            ownerentropy = ownersalt + lotseq
        else:
            if not ownersalt:
                ownersalt = ownerentropy = sha256(seed).digest()[:8]
            else:
                ownerentropy = ownersalt

        prefactor = scrypt.hash(passphrase, ownersalt, 16384, 8, 8, 32)

        if lot and sequence:
            passfactor = sha256(sha256(prefactor + ownerentropy).digest()).digest()
        else:
            passfactor = prefactor

        passpoint = compress(*fast_multiply(G, bytes_to_int(passfactor)))

        last_byte = b'\x53' if not lot and not sequence else b'\x51'

        #                  7                            1            8            33
        payload = b'\x2C\xE9\xB3\xE1\xFF\x39\xE2' + last_byte + ownerentropy + passpoint
        return cls(b58encode_check(payload))


class Bip38ConfirmationCode(Bip38Primitive):

    def __init__(self, b58check):
        if not b58check.startswith('cfrm38'):
            raise Exception("Invalid Confirm code, must start with 'cfrm38'")
        self.b58check = b58check
        payload = b58decode_check(b58check)
        flagbyte = payload[5:6]

        if flagbyte == b'\x20':
            self.compressed = True
            self.sequence_and_lot = False
        elif flagbyte == b'\x00':
            self.compressed = False
            self.sequence_and_lot = False
        elif flagbyte == b'\x04':
            self.compressed = False
            self.sequence_and_lot = True
        elif flagbyte == b'\x24':
            self.compressed = True
            self.sequence_and_lot = True
        else:
            raise Exception("Unknown flagbyte: %s" % flagbyte)

        self.addresshash = payload[6:10] # 4 bytes
        self.ownerentropy = payload[10:18] # 8 bytes
        encryptedpointb = payload[18:] # 33 bytes

        self.pointbprefix = encryptedpointb[0:1] # 1 byte
        self.pointbx1 = encryptedpointb[1:17] # 16 bytes
        self.pointbx2 = encryptedpointb[17:] # 16 bytes

        if self.sequence_and_lot:
            self.ownersalt = self.ownerentropy[:4]
            lotsequence = bytes_to_int(self.ownerentropy[4:]) # 4 bytes
            self.lot = lotsequence // Bip38IntermediatePoint.lotseq_constant
            self.sequence = lotsequence % self.lot
        else:
            self.sequence, self.lot = None, None
            self.ownersalt = self.ownerentropy

    @classmethod
    def create(cls, flagbyte, ownerentropy, factorb, derivedhalf1, derivedhalf2, addresshash):
        pointb = compress(*fast_multiply(G, factorb))
        pointbprefix = bytearray([ord(pointb[:1]) ^ (ord(derivedhalf2[-1:]) & 1)])

        aes = AES.new(derivedhalf2)
        block1 = long(hexlify(pointb[1:17]), 16) ^ long(hexlify(derivedhalf1[:16]), 16)

        pointbx1 = aes.encrypt(unhexlify("%0.32x" % block1))
        block2 = long(hexlify(pointb[17:]), 16) ^ long(hexlify(derivedhalf1[16:]), 16)
        pointbx2 = aes.encrypt(unhexlify("%0.32x" % block2))

        #  33 bytes           1            16         16
        encryptedpointb = pointbprefix + pointbx1 + pointbx2

        #           5 (cfrm38 prefix)          1            4             8               33
        payload = b'\x64\x3B\xF6\xA8\x9A' + flagbyte + addresshash + ownerentropy + encryptedpointb
        return cls(b58encode_check(payload))

    def generate_address(self, passphrase):
        """
        Make sure the confirm code is valid for the given password and address.
        """

        inter = Bip38IntermediatePoint.create(passphrase, ownersalt=self.ownersalt)

        public_key = privtopub(inter.passpoint)

        # from Bip38EncryptedPrivateKey.create_from_intermediate
        derived = scrypt.hash(inter.passpoint, self.addresshash + inter.ownerentropy, 1024, 1, 1, 64)
        derivedhalf1, derivedhalf2 = derived[:32], derived[32:]

        unencrypted_prefix = bytes_to_int(self.pointbprefix) ^ (bytes_to_int(derived[63]) & 0x01);

        aes = AES.new(derivedhalf2)
        block1 = aes.decrypt(self.pointbx1)
        block2 = aes.decrypt(self.pointbx2)

        raise Exception("Not done yet")

        return
        block2 = long(hexlify(pointb2), 16) ^ long(hexlify(derivedhalf1[16:]), 16)


        return pubtoaddr(*fast_multiply(pointb, passfactor))



## tests below


def ec_test():
    """
    Tests the ec-multiply sections. Cases taken from the bip38 document.
    """
    seed = "dh3409sjgh3g48"
    seed2 = "asdas8729akjbmn"

    cases = [[
        'btc',
        'TestingOneTwoThree',
        'passphrasepxFy57B9v8HtUsszJYKReoNDV6VHjUSGt8EVJmux9n1J3Ltf1gRxyDGXqnf9qm',
        '6PfQu77ygVyJLZjfvMLyhLMQbYnu5uguoJJ4kMCLqWwPEdfpwANVS76gTX',
        '1PE6TQi6HTVNz5DLwB1LcpMBALubfuN2z2',
        '5K4caxezwjGCGfnoPTZ8tMcJBLB7Jvyjv4xxeacadhq8nLisLR2',
        ],[
        'btc',
        'Satoshi',
        'passphraseoRDGAXTWzbp72eVbtUDdn1rwpgPUGjNZEc6CGBo8i5EC1FPW8wcnLdq4ThKzAS',
        '6PfLGnQs6VZnrNpmVKfjotbnQuaJK4KZoPFrAjx1JMJUa1Ft8gnf5WxfKd',
        '1CqzrtZC6mXSAhoxtFwVjz8LtwLJjDYU3V',
        '5KJ51SgxWaAYR13zd9ReMhJpwrcX47xTJh2D3fGPG9CM8vkv5sH',
    ]]

    i = 1
    for crypto, passphrase, inter_point, encrypted_pk, address, decrypted_pk in cases:
        test_inter_point = Bip38IntermediatePoint.create(passphrase, seed)
        test_generated_address, test_encrypted_pk, test_cfm = Bip38EncryptedPrivateKey.create_from_intermediate(crypto, test_inter_point, seed2)
        assert test_generated_address == test_cfm.generate_address(passphrase), "Generate address from confirm code failed."
        print("EC multiply test #%s passed!" % i)
        i+= 1


    cases2 = [[
        'btc',
        'MOLON LABE',
        'passphraseaB8feaLQDENqCgr4gKZpmf4VoaT6qdjJNJiv7fsKvjqavcJxvuR1hy25aTu5sX',
        '6PgNBNNzDkKdhkT6uJntUXwwzQV8Rr2tZcbkDcuC9DZRsS6AtHts4Ypo1j',
        '1Jscj8ALrYu2y9TD8NrpvDBugPedmbj4Yh',
        '5JLdxTtcTHcfYcmJsNVy1v2PMDx432JPoYcBTVVRHpPaxUrdtf8',
        'cfrm38V8aXBn7JWA1ESmFMUn6erxeBGZGAxJPY4e36S9QWkzZKtaVqLNMgnifETYw7BPwWC9aPD',
        263183,
        1
        ],[
        'btc',
        u'ΜΟΛΩΝ ΛΑΒΕ',
        'passphrased3z9rQJHSyBkNBwTRPkUGNVEVrUAcfAXDyRU1V28ie6hNFbqDwbFBvsTK7yWVK',
        '6PgGWtx25kUg8QWvwuJAgorN6k9FbE25rv5dMRwu5SKMnfpfVe5mar2ngH',
        '1Lurmih3KruL4xDB5FmHof38yawNtP9oGf',
        '5KMKKuUmAkiNbA3DazMQiLfDq47qs8MAEThm4yL8R2PhV1ov33D',
        'cfrm38V8G4qq2ywYEFfWLD5Cc6msj9UwsG2Mj4Z6QdGJAFQpdatZLavkgRd1i4iBMdRngDqDs51',
        806938,
        1
    ]]

    i = 3
    for crypto, passphrase, inter_point, encrypted_pk, address, decrypted_pk, confirm, lot, sequence in cases2:
        test_inter_point = Bip38IntermediatePoint.create(passphrase, seed)
        test_generated_address, test_encrypted_pk, test_cfm = Bip38EncryptedPrivateKey.create_from_intermediate(crypto, inter_point, seed2)
        cfrm = Bip38ConfirmationCode(confirm)
        print("EC multiply test #%s passed!" % i)
        i += 1


def non_ec_test():
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
    ]]

    index = 1
    for crypto, encrypted_key, unencrypted_key, password, use_wif in cases:
        pk = Bip38EncryptedPrivateKey.encrypt(crypto, unencrypted_key, password)
        assert encrypted_key == str(pk), "encrypt failed"
        assert unencrypted_key == pk.decrypt(password, wif=use_wif), 'decrypt failed'
        print("Non-ec multiply test #%s passed" % index)
        index += 1


def test():
    ec_test()
    #non_ec_test()
