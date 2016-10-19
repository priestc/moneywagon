from datetime import datetime
from .services import *

# instructions for getting version byte:
# https://github.com/MichaelMure/WalletGenerator.net/wiki/How-to-add-a-new-currency#step-two-find-the-prefixes-for-the-address-format-of-your-currency

# also here: https://github.com/MichaelMure/WalletGenerator.net/blob/master/src/janin.currency.js#L78

crypto_data = {
    'btc': {
        'name': 'Bitcoin',
        'address_version_byte': 0,
        'message_magic': 0xd9b4bef9,
        'bip44_coin_type': 0x80000000,
        'private_key_prefix': 128,
        'genesis_date': datetime(2009, 1, 12),
        'services': {
            'current_price': [
                Bitstamp, Winkdex, BTCE, BTER, Cryptonator, ChainSo
            ],
            'address_balance': [
                Toshi, BlockCypher, Blockr, ChainSo,
                BitEasy, SmartBitAU, BlockExplorerCom, BlockChainInfo, Blockonomics,
                BitpayInsight, CoinPrism, BitGo, NeoCrypto
            ],
            'historical_transactions': [
                Blockr, Toshi, BlockExplorerCom, BitGo, SmartBitAU, ChainSo, CoinPrism, BlockSeer,
                BitpayInsight, Blockonomics, NeoCrypto
            ],
            'single_transaction': [
                BitpayInsight, Blockr, BlockChainInfo, Blockonomics, NeoCrypto
            ],
            'push_tx': [
                BlockChainInfo, BlockExplorerCom, Blockr, ChainSo, CoinPrism,
                BitpayInsight, NeoCrypto
            ],
            'unspent_outputs': [
                Blockr, BitpayInsight, BlockExplorerCom, SmartBitAU, BlockChainInfo, CoinPrism, ChainSo,
                BitGo, NeoCrypto
            ],
            'get_block': [
                BitpayInsight, ChainRadar, Toshi, Blockr, BlockExplorerCom, ChainSo, BitGo, NeoCrypto
            ],
            "get_optimal_fee": [
                BitGo, BlockCypher, CoinTape, BitcoinFees21
            ]
        },
    },
    'ltc': {
        'name': 'Litecoin',
        'address_version_byte': 48,
        'bip44_coin_type': 0x80000002,
        'private_key_prefix': 176,
        'genesis_date': datetime(2011, 10, 7),
        'services': {
            'current_price': [
                BTCE, ChainSo, BTER, Cryptonator
            ],
            'address_balance': [
                BlockCypher, Blockr, ChainSo, ProHashing
            ],
            'historical_transactions': [
                ProHashing, Blockr, ChainSo
            ],
            'single_transaction': [
                Blockr
            ],
            'push_tx': [
                Blockr, ChainSo
            ],
            'unspent_outputs': [
                ChainSo, Blockr
            ],
            'get_block': [
                ChainSo, Blockr, ProHashing
            ]
        },
    },
    'ppc': {
        'name': 'Peercoin',
        'address_version_byte': 55,
        'bip44_coin_type': 0x80000006,
        'private_key_prefix': 183,
        'proof_of_stake': True,
        'genesis_date': datetime(2012, 8, 19),
        'services': {
            'current_price': [
                BTCE, ChainSo, BTER, Cryptonator
            ],
            'address_balance': [
                Blockr, Mintr
            ],
            'historical_transactions': [
                Blockr
            ],
            'single_transaction': [
                Mintr, Blockr
            ],
            'push_tx': [
                MultiCoins
            ],
            'unspent_outputs': [
                Blockr
            ],
            'get_block': [
                Blockr, Mintr
            ]
        },
    },
    'doge': {
        'name': 'Dogecoin',
        'address_version_byte': 30,
        'bip44_coin_type': 0x80000003,
        'private_key_prefix': 158,
        'genesis_date': datetime(2013, 12, 6),
        'services': {
            'current_price': [
                BTER, ChainSo, Cryptonator
            ],
            'address_balance': [
                BlockCypher, ChainSo, DogeChainInfo, ProHashing
            ],
            'historical_transactions': [
                BlockCypher, ChainSo, ProHashing
            ],
            'single_transaction': [
                BlockCypher
            ],
            'push_tx': [
                ChainSo
            ],
            'unspent_outputs': [
                DogeChainInfo, ChainSo
            ],
            'get_block': [
                ChainSo, ProHashing
            ]
        },
    },
    'nxt': {
        'name': 'Nxt',
        'address_version_byte': None,
        'bip44_coin_type': 0x8000001d,
        'private_key_prefix': None,
        'genesis_date': datetime(2013, 10, 29),
        'services': {
            'current_price': [
                ChainSo, Cryptonator
            ],
            'address_balance': [
                NXTPortal
            ],
            'historical_transactions': [
                NXTPortal
            ],
            'single_transaction': [

            ],
            'push_tx': [

            ],
            'unspent_outputs': [

            ],
            'get_block': [

            ]
        },
    },
    'myr': {
        'name': 'MyriadCoin',
        'address_version_byte': 50,
        'bip44_coin_type': 0x8000005a,
        'private_key_prefix': 178,
        'genesis_date': datetime(2014, 2, 23),
        'services': {
            'current_price': [
                Cryptonator, ChainSo
            ],
            'address_balance': [
                MYRCryptap, CryptapUS, BirdOnWheels, ProHashing
            ],
            'historical_transactions': [
                MYRCryptap, BirdOnWheels, ProHashing
            ],
            'single_transaction': [
                MYRCryptap, BirdOnWheels
            ],
            'push_tx': [
                MYRCryptap, BirdOnWheels
            ],
            'unspent_outputs': [
                MYRCryptap, BirdOnWheels
            ],
            'get_block': [
                MYRCryptap, BirdOnWheels, ProHashing
            ]
        },
    },
    'vtc': {
        'name': 'Vertcoin',
        'address_version_byte': 71,
        'bip44_coin_type': 0x8000001c,
        'private_key_prefix': 199,
        'genesis_date': datetime(2014, 1, 8),
        'services': {
            'current_price': [
                Cryptonator, ChainSo
            ],
            'address_balance': [
                Verters, ProHashing
            ],
            'historical_transactions': [
                Verters, ProHashing
            ],
            'single_transaction': [
                Verters
            ],
            'push_tx': [
                Verters
            ],
            'unspent_outputs': [
                Verters
            ],
            'get_block': [
                Verters, ProHashing
            ]
        },
    },
    'ftc': {
        'name': 'Feathercoin',
        'address_version_byte': 14,
        'bip44_coin_type': 0x80000008,
        'private_key_prefix': 0x8e,
        'genesis_date': datetime(2013, 4, 16),
        'services': {
            'current_price': [
                ChainSo, Cryptonator
            ],
            'address_balance': [
                ProHashing
            ],
            'historical_transactions': [
                ProHashing
            ],
            'single_transaction': [

            ],
            'push_tx': [

            ],
            'unspent_outputs': [

            ],
            'get_block': [
                ProHashing
            ]
        },
    },
    'dash': {
        'name': 'Dash',
        'address_version_byte': 76,
        'bip44_coin_type': 0x80000005,
        'private_key_prefix': 204,
        'genesis_date': datetime(2014, 1, 19),
        'services': {
            'current_price': [
                ChainSo, Cryptonator
            ],
            'address_balance': [
                ProHashing, CryptoID, SiampmDashInsight
            ],
            'historical_transactions': [
                ProHashing, SiampmDashInsight
            ],
            'single_transaction': [
                SiampmDashInsight
            ],
            'push_tx': [
                SiampmDashInsight
            ],
            'unspent_outputs': [
                SiampmDashInsight
            ],
            'get_block': [
                ProHashing, SiampmDashInsight
            ]
        },
    },
    'rdd': {
        'name': 'Reddcoin',
        'address_version_byte': 61,
        'bip44_coin_type': 0x80000004,
        'private_key_prefix': 0xbd,
        'genesis_date': datetime(2014, 1, 20),
        'proof_of_stake': True,
        'services': {
            'current_price': [
                ChainSo, Cryptonator
            ],
            'address_balance': [
                ReddcoinCom, ProHashing
            ],
            'historical_transactions': [
                ReddcoinCom, ProHashing
            ],
            'single_transaction': [
                ReddcoinCom
            ],
            'push_tx': [
                ReddcoinCom
            ],
            'unspent_outputs': [
                ReddcoinCom
            ],
            'get_block': [
                ReddcoinCom, ProHashing
            ]
        },
    },

    'nmc': {
        'name': 'Namecoin',
        'address_version_byte': 52,
        'bip44_coin_type': 0x80000007,
        'private_key_prefix': 0x80,
        'genesis_date': datetime(2011, 4, 18),
        'services': {
            'current_price': [
                Cryptonator
            ],
        }
    },
    'aur': {
        'name': 'Auroracoin',
        'address_version_byte': 23,
        'bip44_coin_type': 0x80000055,
        'private_key_prefix': 0x97,
        'genesis_date': datetime(2014, 2, 2),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                CryptoID, ProHashing
            ],
            'historical_transactions': [
                ProHashing
            ],
            'single_transaction': [

            ],
            'push_tx': [

            ],
            'unspent_outputs': [
                CryptoID
            ],
            'get_block': [
                ProHashing
            ]
        },
    },

    'emc': {
        'name': 'Emercoin',
        'address_version_byte': 33,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(2011, 11, 5),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                Mintr
            ],
            'historical_transactions': [

            ],
            'single_transaction': [
                Mintr
            ],
            'push_tx': [

            ],
            'unspent_outputs': [

            ],
            'get_block': [
                Mintr
            ]
        },
    },

    'gsm': {
        'name': 'GSMcoin',
        'address_version_byte': 38,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(1, 1, 1),
        'services': {
            'current_price': [

            ],
            'address_balance': [
                BlockExplorersNet
            ],
            'historical_transactions': [

            ],
            'single_transaction': [
                BlockExplorersNet
            ],
            'push_tx': [

            ],
            'unspent_outputs': [

            ],
            'get_block': [
                BlockExplorersNet
            ]
        },
    },

    'erc': {
        'name': 'Europecoin',
        'address_version_byte': 33,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(1, 1, 1),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                BlockExplorersNet
            ],
            'historical_transactions': [

            ],
            'single_transaction': [
                BlockExplorersNet
            ],
            'push_tx': [

            ],
            'unspent_outputs': [

            ],
            'get_block': [
                BlockExplorersNet
            ]
        },
    },

    'tx': {
        'name': 'Transfercoin',
        'address_version_byte': 66,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(1, 1, 1),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                CryptoID, BlockExplorersNet
            ],
            'historical_transactions': [

            ],
            'single_transaction': [

            ],
            'push_tx': [

            ],
            'unspent_outputs': [
                CryptoID
            ],
            'get_block': [

            ]
        },
    },

    'maid': {
        'name': 'MaidSafeCoin',
        'address_version_byte': 0,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(1, 1, 1),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [

            ],
            'historical_transactions': [

            ],
            'single_transaction': [

            ],
            'push_tx': [

            ],
            'unspent_outputs': [

            ],
            'get_block': [

            ]
        },
    },

    'tips': {
        'name': 'FedoraCoin',
        'address_version_byte': 33,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(2013, 12, 21),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                CryptoID
            ],
            'historical_transactions': [

            ],
            'single_transaction': [

            ],
            'push_tx': [

            ],
            'unspent_outputs': [
                CryptoID
            ],
            'get_block': [

            ]
        },
    },

    'karm': {
        'name': 'Karma',
        'address_version_byte': 45,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(2014, 2, 4),
        'services': {
            'current_price': [

            ],
            'address_balance': [
                CryptoID
            ],
            'historical_transactions': [

            ],
            'single_transaction': [

            ],
            'push_tx': [

            ],
            'unspent_outputs': [
                CryptoID
            ],
            'get_block': [

            ]
        },
    },

    'flap': {
        'name': 'FlappyCoin',
        'address_version_byte': 35,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(2014, 2, 14),
        'services': {
            'current_price': [

            ],
            'address_balance': [
                CryptoID
            ],
            'historical_transactions': [

            ],
            'single_transaction': [

            ],
            'push_tx': [

            ],
            'unspent_outputs': [
                CryptoID
            ],
            'get_block': [

            ]
        },
    },

    'pot': {
        'name': 'PotCoin',
        'address_version_byte': 55,
        'bip44_coin_type': 0x80000051,
        'private_key_prefix': None,
        'genesis_date': datetime(2014, 1, 21),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                CryptoID, ProHashing
            ],
            'historical_transactions': [
                ProHashing
            ],
            'single_transaction': [

            ],
            'push_tx': [

            ],
            'unspent_outputs': [
                CryptoID
            ],
            'get_block': [
                ProHashing
            ]
        },
    },

    'bqc': {
        'name': 'BBQcoin',
        'address_version_byte': 85,
        'bip44_coin_type': None,
        'private_key_prefix': 213,
        'genesis_date': datetime(2012, 7, 15),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [

            ],
            'historical_transactions': [

            ],
            'single_transaction': [

            ],
            'push_tx': [

            ],
            'unspent_outputs': [

            ],
            'get_block': [

            ]
        },
    },

    'nvc': {
        'name': 'Novacoin',
        'address_version_byte': 8,
        'bip44_coin_type': 0x80000032,
        'private_key_prefix': 136,
        'genesis_date': datetime(2012, 10, 1),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                CryptapUS
            ],
            'historical_transactions': [

            ],
            'single_transaction': [

            ],
            'push_tx': [

            ],
            'unspent_outputs': [

            ],
            'get_block': [

            ]
        },
    },

    'uno': {
        'name': 'Unobtanium',
        'address_version_byte': 130,
        'bip44_coin_type': 0x8000005c,
        'private_key_prefix': 224,
        'genesis_date': datetime(2013, 10, 17),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                UNOCryptap, CryptoID
            ],
            'historical_transactions': [
                UNOCryptap, CryptoID
            ],
            'single_transaction': [
                UNOCryptap
            ],
            'push_tx': [
                UNOCryptap
            ],
            'unspent_outputs': [
                UNOCryptap, CryptoID
            ],
            'get_block': [
                UNOCryptap
            ]
        },
    },

    'ric': {
        'name': 'Riecoin',
        'address_version_byte': 60,
        'bip44_coin_type': None,
        'private_key_prefix': 128,
        'genesis_date': datetime(1, 1, 1),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                RICCryptap
            ],
            'historical_transactions': [
                RICCryptap
            ],
            'single_transaction': [
                RICCryptap
            ],
            'push_tx': [
                RICCryptap
            ],
            'unspent_outputs': [
                RICCryptap
            ],
            'get_block': [
                RICCryptap
            ]
        },
    },

    'xrp': {
        'name': 'Ripple',
        'genesis_date': datetime(2011, 3, 1),
        'services': {
            'current_price': [
                Cryptonator
            ],
        }
    },

    'hemp': {
        'name': 'Hempcoin',
        'address_version_byte': 40,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(1, 1, 1),
        'services': {
            'current_price': [

            ],
            'address_balance': [
                BlockExperts
            ],
            'historical_transactions': [

            ],
            'single_transaction': [
                BlockExperts
            ],
            'push_tx': [

            ],
            'unspent_outputs': [

            ],
            'get_block': [
                BlockExperts
            ]
        },
    },

    'dope': {
        'name': 'Dopecoin',
        'address_version_byte': 8,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(1, 1, 1),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                BlockExperts
            ],
            'historical_transactions': [

            ],
            'single_transaction': [
                BlockExperts
            ],
            'push_tx': [

            ],
            'unspent_outputs': [

            ],
            'get_block': [
                BlockExperts
            ]
        },
    },

    'dime': {
        'name': 'Dimecoin',
        'address_version_byte': 15,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(2014, 12, 23),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                BlockExperts
            ],
            'historical_transactions': [

            ],
            'single_transaction': [
                BlockExperts
            ],
            'push_tx': [

            ],
            'unspent_outputs': [

            ],
            'get_block': [
                BlockExperts
            ]
        },
    },

    # TEMPLATE
    'xcp': {
        'name': 'CounterParty',
        'address_version_byte': 0,
        'bip44_coin_type': 0x80000009,
        'private_key_prefix': 128,
        'genesis_date': datetime(2014, 1, 2),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                CoinDaddy1, CoinDaddy2, CounterPartyChain
            ],
            'historical_transactions': [
                CoinDaddy1, CoinDaddy2
            ],
            'single_transaction': [
                CoinDaddy1, CoinDaddy2
            ],
            'push_tx': [
                CoinDaddy1, CoinDaddy2
            ],
            'unspent_outputs': [
                CoinDaddy1
            ],
            'get_block': [
                CoinDaddy1, CoinDaddy2
            ]
        },
    },

    'eth': {
        'name': 'Ethereum',
        'address_version_byte': None,
        'bip44_coin_type': 60,
        'private_key_prefix': None,
        'genesis_date': datetime(2015, 7, 30),
        'services': {
            'current_price': [
                EtherChain
            ],
            'address_balance': [
                EtherChain
            ],
            'historical_transactions': [

            ],
            'single_transaction': [

            ],
            'push_tx': [

            ],
            'unspent_outputs': [

            ],
            'get_block': [

            ]
        },
    },

    # TEMPLATE
    '': {
        'name': '',
        'address_version_byte': None,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(1, 1, 1),
        'services': {
            'current_price': [

            ],
            'address_balance': [

            ],
            'historical_transactions': [

            ],
            'single_transaction': [

            ],
            'push_tx': [

            ],
            'unspent_outputs': [

            ],
            'get_block': [

            ]
        },
    },

    # these ones below need to be modified to match the above format
    # taken from http://coinwik.org/List_of_all_DCs
    # sorted by date released, copied over on Nov 27, 2014

    'tk':  ['TimeKoin', datetime(2011, 5, 27)],
    'dvc': ['DevCoin', datetime(2011, 8, 5)],
    'ixc': ['IxCoin', datetime(2011, 8, 10)],
    'bcn': ['Bytecoin', datetime(2012, 7, 4)],
    'bte': ['Bytecoin', datetime(2012, 7, 4)],
    'str': ['StarCoin', datetime(2012, 7, 19)],
    'trc': ['TerraCoin', datetime(2012, 10, 26)],
    'frc': ['Freicoin', datetime(2012, 12, 21)],
    'btb': ['BitBar', datetime(2013, 4, 1)],
    'mnc': ['MinCoin', datetime(2013, 4, 3)],
    'net': ['NetCoin', datetime(2013, 4, 7)],
    'nan': ['NanoToken', datetime(2013, 4, 8)],
    'pxc': ['PhoenixCoin', datetime(2013, 5, 1)],
    'cnc': ['CHNCoin', datetime(2013, 5, 1)],
    'jkc': ['JunkCoin', datetime(2013, 5, 4)],
    'yac': ['YaCoin', datetime(2013, 5, 5)],
    'ryc': ['RoyalCoin', datetime(2013, 5, 9)],
    'onc': ['OneCoin', datetime(2013, 5, 9)],
    'frk': ['Franko', datetime(2013, 5, 11)],
    'gme': ['GameCoin', datetime(2013, 5, 12)],
    'pwc': ['PowerCoin', datetime(2013, 5, 13)],
    'elc': ['ElaCoin', datetime(2013, 5, 13)],
    'btg': ['BitGem', datetime(2013, 5, 16)],
    'dbl': ['Doubloons', datetime(2013, 5, 16)],
    'dgc': ['DigitalCoin', datetime(2013, 5, 18)],
    'nbl': ['Nibble', datetime(2013, 5, 18)],
    'pxc': ['PhenixCoin', datetime(2013, 5, 20)],
    'wdc': ['WorldCoin', datetime(2013, 5, 22)],
    'lky': ['LuckyCoin', datetime(2013, 5, 24)],
    'mem': ['MemeCoin', datetime(2013, 5, 27)],
    'hyc': ['HyperCoin', datetime(2013, 5, 28)],
    'sxc': ['SexCoin', datetime(2013, 5, 28)],
    'mex': ['MegaCoin', datetime(2013, 5, 29)],
    'fst': ['FastCoin', datetime(2013, 5, 29)],
    'amc': ['AmericanCoin', datetime(2013, 5, 29)],
    'ezc': ['EZCoin', datetime(2013, 5, 29)],
    'ifc': ['InfiniteCoin', datetime(2013, 6, 5)],
    'crc': ['CraftCoin', datetime(2013, 6, 5)],
    'anc': ['AnonCoin', datetime(2013, 6, 6)],
    'nrb': ['NoirBits', datetime(2013, 6, 6)],
    'clr': ['CopperLark', datetime(2013, 6, 6)],
    'rec': ['RealCoin', datetime(2013, 6, 6)],
    'sbc': ['StableCoin', datetime(2013, 6, 7)],
    'alf': ['AlphaCoin', datetime(2013, 6, 9)],
    'gld': ['GoldCoin', datetime(2013, 6, 11)],
    'arg': ['Argentum', datetime(2013, 6, 11)],
    'emd': ['Emerald', datetime(2013, 6, 16)],
    'xnc': ['XenCoin', datetime(2013, 6, 19)],
    'rch': ['Richcoin', datetime(2013, 6, 20)],
    'cap': ['BottleCaps', datetime(2013, 6, 23)],
    'nuc': ['Nucoin', datetime(2013, 6, 24)],
    'glc': ['GlobalCoin', datetime(2013, 6, 26)],
    'cgb': ['CryptogenicBullion', datetime(2013, 6, 27)],
    'cmc': ['CosmosCoin', datetime(2013, 6, 28)],
    'kgc': ['KrugerCoin', datetime(2013, 6, 30)],
    'red': ['RedCoin', datetime(2013, 6, 30)],
    'xpm': ['Primecoin', datetime(2013, 7, 7)],
    'glx': ['GalaxyCoin', datetime(2013, 7, 8)],
    'dmd': ['Diamond', datetime(2013, 7, 13)],
    'gdc': ['GrandCoin', datetime(2013, 7, 13)],
    'mst': ['MasterCoin (Hydro)', datetime(2013, 7, 13)],
    'gil': ['GilCoin', datetime(2013, 7, 14)],
    'elp': ['ElephantCoin', datetime(2013, 7, 15)],
    'flo': ['FlorinCoin', datetime(2013, 7, 17)],
    'csc': ['CasinoCoin', datetime(2013, 7, 18)],
    'qrk': ['Quark', datetime(2013, 7, 21)],
    'lbw': ['LEBOWSKIS', datetime(2013, 7, 21)],
    'hbn': ['Hobonickels', datetime(2013, 7, 24)],
    'nec': ['NeoCoin', datetime(2013, 7, 27)],
    'phs': ['PhilosopherStone', datetime(2013, 7, 28)],
    'msc': ['MasterCoin', datetime(2013, 7, 31)],
    'orb': ['OrbitCoin', datetime(2013, 7, 31)],
    'zet': ['ZetaCoin', datetime(2013, 8, 3)],
    'cent':['Pennies', datetime(2013, 8, 4)],
    'pyc': ['PayCoin', datetime(2013, 8, 6)],
    'zcc': ['ZCCoin', datetime(2013, 8, 7)],
    'cpr': ['CopperBars', datetime(2013, 8, 11)],
    'exc': ['Extremecoin', datetime(2013, 8, 17)],
    'adt': ['AndroidsTokens', datetime(2013, 8, 18)],
    'col': ['ColossusCoin', datetime(2013, 8, 22)],
    'i0c': ['I0Coin', datetime(2013, 8, 27)],
    'src': ['SecureCoin', datetime(2013, 8, 28)],
    'tgc': ['TigerCoin', datetime(2013, 9, 6)],
    'tek': ['TekCoin', datetime(2013, 9, 7)],
    'asc': ['AsicCoin', datetime(2013, 9, 11)],
    'lk7': ['Lucky7Coin', datetime(2013, 9, 15)],
    'tix': ['Tickets', datetime(2013, 9, 19)],
    'xjo': ['JouleCoin', datetime(2013, 9, 22)],
    'buk': ['CryptoBuck', datetime(2013, 9, 25)],
    'dem': ['eMark', datetime(2013, 10, 12)],
    'grc': ['GridCoin', datetime(2013, 10, 17)],
    'spt': ['Spots', datetime(2013, 10, 18)],
    'tag': ['TagCoin', datetime(2013, 10, 24)],
    'bet': ['BetaCoin', datetime(2013, 10, 24)],
    'ffc': ['FireFlyCoin', datetime(2013, 10, 25)],
    'osc': ['OpenSourceCoin', datetime(2013, 11, 4)],
    'pts': ['Bitshares-PTS', datetime(2013, 11, 5)],
    'naut':['Nautiluscoin', datetime(2013, 11, 5)],
    'pts': ['ProtoShares', datetime(2013, 11, 5)],
    'apc': ['Applecoin', datetime(2013, 11, 19)],
    'cin': ['Cinnamoncoin', datetime(2013, 11, 21)],
    'ybc': ['YBCoin', datetime(2013, 11, 23)],
    'gra': ['Grain', datetime(2013, 12, 7)],
    'fz':  ['Frozen', datetime(2013, 12, 10)],
    'lot': ['LottoCoin', datetime(2013, 12, 12)],
    'mmc': ['Memorycoin', datetime(2013, 12, 15)],
    'dtc': ['Datacoin', datetime(2013, 12, 17)],
    'xiv': ['Xivra', datetime(2013, 12, 18)],
    'ato': ['AtomCoin', datetime(2013, 12, 22)],
    'cat': ['CatCoin', datetime(2013, 12, 23)],
    'meow':['KittehCoin', datetime(2013, 12, 24)],
    'moon':['MoonCoin', datetime(2013, 12, 28)],
    'qqc': ['QQcoin', datetime(2013, 12, 28)],
    'rpc': ['RonPaulCoin', datetime(2013, 12, 29)],
    'vel': ['Velocitycoin', datetime(2013, 12, 29)],
    'eac': ['EarthCoin', datetime(2013, 12, 31)],
    'prt': ['Particle', datetime(2013, 12, 31)],
    'mona':['MonaCoin', datetime(2013, 12, 31)],
    'slr': ['SolarCoin', datetime(2014, 1, 1)],
    'volt':['Electric', datetime(2014, 1, 2)],
    '42':  ['42Coin', datetime(2014, 1, 4)],
    'pnd': ['Pandacoin', datetime(2014, 1, 4)],
    'nut': ['NutCoin', datetime(2014, 1, 4)],
    'cach':['Cachecoin', datetime(2014, 1, 5)],
    'nyan':['Nyancoin', datetime(2014, 1, 5)],
    'smc': ['Smartcoin', datetime(2014, 1, 6)],
    'stc': ['StockCoin', datetime(2014, 1, 6)],
    'nobl':['Noblecoin', datetime(2014, 1, 7)],
    'ptc': ['PesetaCoin', datetime(2014, 1, 7)],
    'aph': ['AphroditeCoin', datetime(2014, 1, 7)],
    'rpd': ['Rapidcoin', datetime(2014, 1, 8)],
    'etok':['Etoken', datetime(2014, 1, 8)],
    'kdc': ['Klondike', datetime(2014, 1, 9)],
    'pir': ['PirateCoin', datetime(2014, 1, 9)],
    'dgb': ['Digibyte', datetime(2014, 1, 10)],
    'xc':  ['XCurrency', datetime(2014, 1, 10)],
    'bcx': ['BattleCoin', datetime(2014, 1, 10)],
    'icn': ['iCoin', datetime(2014, 1, 10)],
    'krn': ['Ekrona', datetime(2014, 1, 10)],
    'usde':['Unitary Status Dollar eCoin', datetime(2014, 1, 12)],
    'q2c': ['Qubitcoin', datetime(2014, 1, 12)],
    'zed': ['ZedCoin', datetime(2014, 1, 14)],
    'mtc': ['MarineCoin', datetime(2014, 1, 15)],
    'fox': ['FoxCoin', datetime(2014, 1, 17)],
    'tes': ['Teslacoin', datetime(2014, 1, 18)],
    'con': ['Coino', datetime(2014, 1, 18)],
    'plc': ['PolCoin', datetime(2014, 1, 19)],
    'cash':['CashCoin', datetime(2014, 1, 20)],
    'mry': ['MurrayCoin', datetime(2014, 1, 20)],
    'asr': ['AstroCoin', datetime(2014, 1, 21)],
    'pmc': ['Premine', datetime(2014, 1, 23)],
    'leaf':['LeafCoin', datetime(2014, 1, 24)],
    '66':  ['66Coin', datetime(2014, 1, 26)],
    'tea': ['Teacoin', datetime(2014, 1, 27)],
    'huc': ['Huntercoin', datetime(2014, 1, 27)],
    'top': ['Topcoin', datetime(2014, 1, 27)],
    'max': ['Maxcoin', datetime(2014, 1, 29)],
    'utc': ['Ultracoin', datetime(2014, 2, 1)],
    'ben': ['Benjamins', datetime(2014, 2, 1)],
    'pop': ['PopularCoin', datetime(2014, 2, 2)],
    'lbt': ['Litebar', datetime(2014, 2, 2)],
    'corg':['CorgiCoin', datetime(2014, 2, 2)],
    'hex': ['Heisenberg', datetime(2014, 2, 5)],
    'wtc': ['World Top Coin', datetime(2014, 2, 5)],
    'mint':['Mintcoin', datetime(2014, 2, 6)],
    'trl': ['TrollCoin', datetime(2014, 2, 7)],
    'sochi':['SochiCoin', datetime(2014, 2, 7)],
    'tak': ['TakeiCoin', datetime(2014, 2, 8)],
    'lyc': ['LycanCoin', datetime(2014, 2, 8)],
    'snp': ['SnapCoin', datetime(2014, 2, 9)],
    'lmc': ['LemonCoin', datetime(2014, 2, 9)],
    'akc': ['Anti-Keiser-Coin', datetime(2014, 2, 10)],
    'bee': ['BeeCoin', datetime(2014, 2, 12)],
    'epc': ['EmperorCoin', datetime(2014, 2, 13)],
    'doug':['DougCoin', datetime(2014, 2, 13)],
    'mim': ['Magic Internet Money', datetime(2014, 2, 13)],
    'loot':['Crypto LOOT', datetime(2014, 2, 13)],
    'note':['DNotes', datetime(2014, 2, 16)],
    'che': ['RevolutionCoin', datetime(2014, 2, 16)],
    'eqb': ['EquestrianBit', datetime(2014, 2, 17)],
    'v':   ['Version', datetime(2014, 2, 21)],
    'btq': ['BitQuark', datetime(2014, 2, 22)],
    'app': ['AppCoin', datetime(2014, 2, 23)],
    'bc':  ['BlackCoin', datetime(2014, 2, 24)],
    'mzc': ['MazaCoin', datetime(2014, 2, 24)],
    'blc': ['Blakecoin', datetime(2014, 2, 24)],
    'edu': ['EduCoin', datetime(2014, 2, 25)],
    'crd': ['Credits', datetime(2014, 2, 25)],
    'exe': ['EXECoin', datetime(2014, 2, 27)],
    'ccn': ['C-Coin', datetime(2014, 2, 27)],
    'zeit':['Zeitcoin', datetime(2014, 2, 28)],
    'uvc': ['UniversityCoin', datetime(2014, 2, 28)],
    'gox': ['MtgoxCoin', datetime(2014, 2, 28)],
    'emc2':['Einsteinium', datetime(2014, 3, 1)],
    'ddc': ['DokdoCoin', datetime(2014, 3, 1)],
    'flt': ['Fluttercoin', datetime(2014, 3, 5)],
    '888': ['OctoCoin', datetime(2014, 3, 8)],
    'fail':['FailCoin', datetime(2014, 3, 8)],
    'ghc': ['Ghostcoin', datetime(2014, 3, 10)],
    'blitz':['BlitzCoin', datetime(2014, 3, 10)],
    'diem':['Carpe Diem', datetime(2014, 3, 13)],
    'grs': ['GroestlCoin', datetime(2014, 3, 22)],
    'crypt':['CryptCoin', datetime(2014, 3, 25)],
    'comm':['Communitycoin', datetime(2014, 3, 25)],
    'sha': ['Sha1Coin', datetime(2014, 3, 28)],
    'wc':  ['Whitecoin', datetime(2014, 4, 4)],
    'adn': ['Aiden', datetime(2014, 4, 5)],
    'xlb': ['LibertyCoin', datetime(2014, 4, 5)],
    'ac':  ['AsiaCoin', datetime(2014, 4, 16)],
    'xmr': ['Monero', datetime(2014, 4, 18)],
    'cinni':['CinniCoin', datetime(2014, 4, 19)],
    'bst': ['GlobalBoost', datetime(2014, 4, 27)],
    'mon': ['Monocle', datetime(2014, 5, 2)],
    'cure':['Curecoin', datetime(2014, 5, 2)],
    'vrc': ['Vericoin', datetime(2014, 5, 10)],
    'nyc': ['NewYorkCoin', datetime(2014, 5, 21)],
    'shc': ['SherlockCoin', datetime(2014, 5, 28)],
    'cloak':['Cloakcoin', datetime(2014, 5, 31)],
    'trk': ['Truckcoin', datetime(2014, 6, 3)],
    'min': ['Minerals', datetime(2014, 6, 5)],
    'stl': ['STLCoin', datetime(2014, 6, 25)],
    'met': ['MetaCoin', datetime(2014, 7, 4)],
    'str': ['Stellar', datetime(2014, 7, 31)],
    'pxl': ['Pixelcoin', datetime(2014, 11, 1)],
    'pac': ['PacCoin', datetime(2014, 12, 12)],
}


# don't have launch dates for these...
#
# RubyCoin	RUBY	Date	POW Scrypt	60 Million Coins	M F E W	x
# SaturnCoin	SAT2	Date	POW Scrypt	7,777,777 Coins	M F E W	x
# Grumpycoin	GRUMP	Date	POW Scrypt	20 Billion Coins	M F E W	x
# XXLCOIN	XXL	Date	POW Scrypt	2800 Billion Coins	M F E W	x
# Stories	STY	Date	POW SHA256	60 Million Coins	M F E W	x
# PolishCoin	PCC	Date	POW Scrypt	150 Million Coins	M F E W	x
# AnimeCoin	ANI	Date	Quark Algo	1.976 Billion	M F E W	x
# BillionCoin	BIL	Date	Scrypt Algo	10 Billion	M F E W	x
# 365Coin	365	Date	SHA3 Keccak	365 Coins	M F E W	x
# PLNCoin	PLNC	Date	Scrypt Algo	38,540,000 Coins	M F E W	x
# SovereignCoin	SVC	Date	Type	Supply	M F E W	x
# 84Coin	84	Date	POW Scrypt	84 Coins	M F E W	x
# CrimeaCoin	CMA	Date	Type	100 Million	M F E W	x
# FckBanks	FCK	Date	POW Scrypt	84 Billion	M F E W	x
# BeliCoin	BELI	Date	POW/POS Scrypt	900 Billion	M F E W	x
# GPUCoin	GPUC	Date	POW Scrypt	13.5 Billion	M F E W	x
# RealStackCoin	RSC	Date	POW Scrypt Algo	134.4 Billion	M F E W	x
# W2Coin	W2C	2014	POW Scrypt	2.1 Billion Coins	M F E W	9300
# Riecoin', datetime(201402	POW prime constellations	84 Million coins	M F E W	x
# Maidsafecoin	SAFE	20060222	POR
