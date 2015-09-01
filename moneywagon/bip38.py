import sys
from Crypto.Cipher import AES
from binascii import unhexlify, hexlify
from bitcoin import privtopub, pubtoaddr, encode_privkey, get_privkey_format, sha256

try:
    import scrypt
except ImportError:
    raise ImportError("Scrypt is required for BIP38 support: pip install scrypt")

try:
    from base58 import b58decode, b58encode
except ImportError:
    raise ImportError("Base58 is required: pip install base58")
