from datetime import datetime
from .services import *
from moneywagon.core import make_standard_halfing_eras

# instructions for getting version byte:
# https:/github.com/MichaelMure/WalletGenerator.net/wiki/How-to-add-a-new-currency#step-two-find-the-prefixes-for-the-address-format-of-your-currency

# also here: https://github.com/MichaelMure/WalletGenerator.net/blob/master/src/janin.currency.js#L78

crypto_data = {
    'btc': {
        'name': 'Bitcoin Legacy',
        'address_version_byte': 0, # base58Prefixes[PUBKEY_ADDRESS] in chainparams.cpp
        'message_magic': b"\xf9\xbe\xb4\xd9", # pchMessageStart in chainparams.cpp
        'bip44_coin_type': 0x80000000,
        'private_key_prefix': 128,  # base58Prefixes[SECRET_KEY] in chainparams.cpp
        'script_hash_byte': 0x05, # base58Prefixes[SCRIPT_ADDRESS] in chainparams.cpp
        'genesis_date': datetime(2009, 1, 3, 18, 15, 5),
        'header_hash_algo': 'double-sha256',
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'github_link': "https://github.com/Bitcoin/bitcoin",
        'port': 8333,
        'seed_nodes': [
            "seed.b-pay.net",
            "seed.ob1.io"
            "seed.blockchain.info",
            "seed.bloq.com",
        ],
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 50,
            'minutes_per_block': 10,
            'full_cap': 21000000,
            'blocks_per_era': 210000,
            'reward_ends_at_block': 6930000
        },
        'services': {
            'current_price': {
                'usd': [
                    Bitstamp, GDAX, Wex, Gemini, Huobi, Bittrex, CexIO, YoBit,
                    Poloniex, Winkdex, ChainSo, Kraken, BitFinex, xBTCe, Vircurex,
                    HitBTC, LiveCoin, BitFlyer, ItBit, KuCoin, CCex, OKEX, BitZ, ZB,
                    EXX, Bibox
                ],
                'cny': [BTER, BTCChina, Huobi, ViaBTC, xBTCe, BTC38, ChainSo],
                'rur': [Wex, LiveCoin], 'jpy': [BitFlyer, Kraken, xBTCe, Zaif, BitBank],
                'gbp': [Kraken, xBTCe],
                'eur': [Bitstamp, HitBTC, xBTCe, UseCryptos, LiveCoin, Kraken, ChainSo, ItBit],
                'cad': [Kraken], 'zar': [BitX], 'myr': [BitX], 'ngn': [BitX],
                'idr': [BitcoinIndonesia, BitX], 'mxn': [Bitso], 'bgn': [CryptoBG],
                'krw': [CoinOne, CoinNest], 'sgd': [ItBit], '*': [Cryptonator, Yunbi]
            },
            'address_balance': [
                BlockCypher, ChainSo,
                BitEasy, SmartBitAU, BlockExplorerCom, BlockChainInfo, Blockonomics,
                BitpayInsight, CoinPrism, BitGo, LocalBitcoinsChain, Bchain
            ],
            'historical_transactions': [
                BlockExplorerCom, BitGo, SmartBitAU, ChainSo, CoinPrism, BlockSeer,
                BitpayInsight, Blockonomics, LocalBitcoinsChain
            ],
            'single_transaction': [
                BitpayInsight, BlockCypher, BlockExplorerCom,
                ChainSo, CoinPrism, SmartBitAU, LocalBitcoinsChain
            ],
            'push_tx': [
                BlockChainInfo, BlockExplorerCom, ChainSo, CoinPrism,
                BitpayInsight, LocalBitcoinsChain
            ],
            'unspent_outputs': [
                BitpayInsight, BlockExplorerCom, SmartBitAU, BlockChainInfo, CoinPrism, ChainSo,
                BitGo, LocalBitcoinsChain
            ],
            'get_block': [
                BitpayInsight, ChainRadar, OKcoin, BlockExplorerCom, ChainSo,
                BitGo, LocalBitcoinsChain, BitFlyer
            ],
            "get_optimal_fee": [
                BitGo, BlockCypher, CoinTape, BitcoinFees21
            ]
        },
    },
    'ltc': {
        'name': 'Litecoin',
        'address_version_byte': 48,
        'message_magic': b"\xfb\xc0\xb6\xdb",
        'bip44_coin_type': 0x80000002,
        'private_key_prefix': 176,
        'script_hash_byte': 50,
        'genesis_date': datetime(2011, 10, 7),
        'header_hash_algo': 'scrypt',
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': 9333,
        'seed_nodes': [
            'dnsseed.litecointools.com',
            'dnsseed.litecoinpool.org',
            'dnsseed.ltc.xurious.com',
            'dnsseed.koin-project.com',
            'dnsseed.weminemnc.com'
        ],
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 50,
            'minutes_per_block': 2.5,
            'full_cap': 84000000,
            'blocks_per_era': 840000
        },
        'services': {
            'current_price': {
                'usd': [
                    Wex, GDAX, Poloniex, Kraken, Cryptopia, ChainSo, OKEX,
                    xBTCe, YoBit, UseCryptos, HitBTC, LiveCoin, BitFinex, CCex,
                    EXX, Bibox
                ],
                'cny': [Wex, Huobi, BTER, xBTCe, ViaBTC, ChainSo, OKcoin, BTC38, BTCChina],
                'rur': [YoBit, xBTCe], 'eur': [Kraken, HitBTC, Wex, GDAX, UseCryptos, xBTCe],
                'btc': [
                    GDAX, Wex, BTER, BleuTrade, HitBTC, Bittrex, Poloniex,
                    ChainSo, xBTCe, YoBit, Cryptopia, Kraken, NovaExchange, BitFinex,
                    BitcoinIndonesia, BTCChina, Liqui, LiveCoin, CryptoDao, KuCoin,
                    CCex, OKEX, BitZ, CoinEgg, ZB, BitBank, EXX, Bibox
                ],
                'doge': [CCex], 'xmr': [Poloniex], 'jpy': [xBTCe], 'nzd': [Cryptopia],
                '*': [Cryptonator, Vircurex], 'qc': [EXX], 'eth': [Bibox]
            },
            'address_balance': [
                BlockCypher, Litecore, ChainSo, ProHashing, HolyTransaction, Bchain
            ],
            'historical_transactions': [
                ProHashing, ChainSo, Litecore
            ],
            'single_transaction': [
                BlockCypher, Litecore
            ],
            'push_tx': [
                ChainSo, Litecore
            ],
            'unspent_outputs': [
                Litecore, ChainSo
            ],
            'get_block': [
                ChainSo, OKcoin, ProHashing, Litecore, HolyTransaction
            ],
            "get_optimal_fee": [
                BlockCypher
            ]
        },
    },
    'ppc': {
        'name': 'Peercoin',
        'address_version_byte': 55,
        'message_magic': b"\xe6\xe8\xe9\xe5",
        'bip44_coin_type': 0x80000006,
        'private_key_prefix': 183,
        'genesis_date': datetime(2012, 8, 19, 18, 12, 4),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'transaction_form': 'ppc-timestamp',
        'github_link': "https://github.com/peercoin/peercoin",
        'port': 9901,
        'supply_data': {
            'method': 'standard',
            'minutes_per_block': 8.2
        },
        'services': {
            'current_price': {
                'usd': [Wex, xBTCe, ChainSo, LiveCoin], 'eur': [UseCryptos],
                'btc': [
                    Wex, xBTCe, BleuTrade, ChainSo, Bittrex, BTER, Poloniex, Vircurex,
                    YoBit, UseCryptos, BitZ
                ], 'doge': [BleuTrade], 'cny': [BTC38],
                '*': [Cryptonator]
            },
            'address_balance': [CryptoID, Mintr, HolyTransaction],
            'historical_transactions': [],
            'single_transaction': [Mintr],
            'push_tx': [MultiCoins],
            'unspent_outputs': [],
            'get_block': [Mintr, HolyTransaction]
        },
    },
    'doge': {
        'name': 'Dogecoin',
        'message_magic': b"\xc0\xc0\xc0\xc0",
        'address_version_byte': 30,
        'bip44_coin_type': 0x80000003,
        'private_key_prefix': 158,
        'script_hash_byte': 0x16,
        'genesis_date': datetime(2013, 12, 6, 10, 25, 40),
        'header_hash_algo': 'scrypt',
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': 22556,
        'seed_nodes': [
            'seed.dogecoin.com',
            'seed.mophides.com',
            'seed.dglibrary.org',
            'seed.dogechain.info'
        ],
        'github_link': "https://github.com/dogecoin/dogecoin",
        'supply_data': {
            'method': 'per_era',
            'eras': [
                {'start': 1,      'end': 100000, 'reward': 500000}, # reward was random, average used
                {'start': 100001, 'end': 144999, 'reward': 250011}, # reward was random, average used
                {'start': 145000, 'end': 200000, 'reward': 250000},
                ] + make_standard_halfing_eras(
                    start=200000, interval=100000,
                    start_reward=125000, total_eras=4
                ) + [
                {'start': 600001, 'end': None,   'reward': 10000}
            ],
            'minutes_per_block': 1.0,
            'full_cap': None,
        },
        'services': {
            'current_price': {
                'usd': [CCex, HitBTC, LiveCoin], 'cny': [BTC38],
                'rur': [YoBit], 'ltc': [NovaExchange],
                'btc': [
                    Bittrex, Poloniex, BleuTrade, ChainSo, BTER, YoBit, HitBTC,
                    NovaExchange, Vircurex, BitcoinIndonesia, UseCryptos, LiveCoin,
                    BitZ, CoinEgg
                ],
                '*': [Cryptonator],
            },
            'address_balance': [
                BlockCypher, ChainSo, DogeChainInfo, ProHashing, HolyTransaction,
                Bchain
            ],
            'historical_transactions': [
                BlockCypher, ChainSo, ProHashing
            ],
            'single_transaction': [
                BlockCypher, ChainSo
            ],
            'push_tx': [
                ChainSo
            ],
            'unspent_outputs': [
                DogeChainInfo, ChainSo
            ],
            'get_block': [
                ChainSo, ProHashing, HolyTransaction
            ]
        },
    },
    'nxt': {
        'name': 'Nxt',
        'address_version_byte': None,
        'bip44_coin_type': 0x8000001d,
        'private_key_prefix': None,
        'genesis_date': datetime(2013, 10, 29),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'transaction_form': 'nxt',
        'port': None,
        'services': {
            'current_price': {
                'btc': [
                    Bittrex, BitcoinIndonesia, HitBTC, ChainSo, Poloniex,
                    LiveCoin, CoinEgg
                ],
                '*': [Cryptonator], 'cny': [BTC38], 'usd': [HitBTC],
            },
            'address_balance': [MyNXT, NXTPortal],
            'historical_transactions': [NXTPortal],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        },
    },
    'xmy': {
        'name': 'MyriadCoin',
        'address_version_byte': 50,
        'message_magic': b"\xaf\x45\x76\xee",
        'bip44_coin_type': 0x8000005a,
        'private_key_prefix': 178,
        'script_hash_byte': 9,
        'genesis_date': datetime(2014, 2, 23),
        'transaction_form': 'cryptonote',
        'port': None,
        'github_link': "https://github.com/myriadteam/myriadcoin",
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 1000,
            'minutes_per_block': 0.5,
            'full_cap': 2000000000,
            'blocks_per_era': 967680
        },
        'services': {
            'current_price': {
                'btc': [Bittrex, Cryptopia], 'ltc': [Cryptopia],
                'doge': [Cryptopia], 'uno': [Cryptopia],
                '*': [Cryptonator]
            },
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
        'message_magic': b"\xfa\xbf\xb5\xda",
        'bip44_coin_type': 0x8000001c,
        'private_key_prefix': 199,
        'genesis_date': datetime(2014, 1, 8),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 50,
            'minutes_per_block': 2.5,
            'full_cap': 84000000,
            'blocks_per_era': 840000
        },
        'services': {
            'current_price': {
                'btc': [Poloniex, Bittrex, ChainSo, BleuTrade, YoBit, CoinEgg],
                'doge': [BleuTrade],
                '*': [Cryptonator],
            },
            'address_balance': [VertcoinInfo, Bchain, VTConline],
            'historical_transactions': [VTConline],
            'single_transaction': [VertcoinInfo, VTConline],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [VertcoinInfo, VTConline]
        },
    },
    'ftc': {
        'name': 'Feathercoin',
        'address_version_byte': 14,
        'message_magic': b"\xfb\xc0\xb6\xdb",
        'bip44_coin_type': 0x80000008,
        'private_key_prefix': 0x8e,
        'genesis_date': datetime(2013, 4, 16),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'per_era',
            'minutes_per_block': 2.5,
            'eras': [
                {'start': 0,      'end': 204638, 'reward': 200},
                {'start': 204639, 'end': 2100000, 'reward': 80}
            ] + make_standard_halfing_eras(
                start=2100000, interval=2100000,
                start_reward=40
            ),
            'blocktime_adjustments': [
                [0, 2.632061418725984],
                [204639, 1]
            ],
            'full_cap': 336000000,
            'blocks_per_era': 2100000,
        },
        'services': {
            'current_price': {
                'btc': [Bittrex, ChainSo, Cryptonator, Vircurex],
                'ltc': [Cryptopia], 'doge': [Cryptopia], 'uno': [Cryptopia],
                '*': [Cryptonator]
            },
            'address_balance': [
                ChainTips, FeathercoinCom2, Bchain
            ],
            'historical_transactions': [
                ChainTips, ProHashing
            ],
            'single_transaction': [
                ChainTips
            ],
            'push_tx': [
                ChainTips
            ],
            'unspent_outputs': [
                ChainTips
            ],
            'get_block': [
                ChainTips, ProHashing
            ]
        },
    },
    'dash': {
        'name': 'Dash',
        'address_version_byte': 76,
        "message_magic": b"\xbf\x0c\x6b\xbd",
        'bip44_coin_type': 0x80000005,
        'private_key_prefix': 204,
        'genesis_date': datetime(2014, 1, 19, 1, 40, 18),
        'header_hash_algo': 'x11',
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': 9999,
        'seed_nodes': [
            'dnsseed.darkcoin.io',
            'dnsseed.dashdot.io',
            'dnsseed.masternode.io',
            'dnsseed.dashpay.io'
        ],
        'supply_data': {
            'method': 'per_era',
            'eras': [
                {'start': 1,   'end': 5000,  'reward': 500}, # "instamine"
                {'start': 5001, 'end': 20000,  'reward': 144},
                {'start': 20001, 'end': 60000, 'reward': 14}
            ] + make_standard_halfing_eras(
                start=60000, interval=210240,
                start_reward=5, halfing_func=lambda era, reward: reward - ((reward/14) * era)
            ),
            'additional_block_interval_adjustment_points': [
                 100, 500, 1000, 3000, 5000
            ],
            'minutes_per_block': 2.5,
            'full_cap': 18900000,
        },
        'services': {
            'current_price': {
                'usd': [
                    HitBTC, CexIO, Cryptopia, BitFinex, Kraken, LiveCoin, xBTCe, Liqui,
                    CCex, ZB, Bibox
                ],
                'doge': [NovaExchange, Cryptopia, BleuTrade], 'eth': [Liqui, HitBTC, Bibox],
                'rur': [YoBit], 'ltc': [NovaExchange, Cryptopia, CCex], 'gdp': [CexIO],
                'btc': [
                    Bittrex, Poloniex, Cryptopia, ChainSo, YoBit, CexIO, BleuTrade,
                    NovaExchange, Kraken, UseCryptos, Liqui, HitBTC, LiveCoin,
                    CryptoDao, BitFinex, CCex, BitZ, ZB, Bibox
                ], 'cny': [xBTCe, BTC38], 'eur': [UseCryptos, Kraken],
                '*': [Cryptonator], 'uno': [Cryptopia], 'moon': [NovaExchange]
            },
            'address_balance': [
                CryptoID, ProHashing, MasterNodeIO, SiampmDashInsight, HolyTransaction,
                DashOrgInsight, DashBlockExplorer
            ],
            'historical_transactions': [
                ProHashing, DashOrgInsight, SiampmDashInsight, MasterNodeIO,
                DashBlockExplorer
            ],
            'single_transaction': [
                DashOrgInsight, SiampmDashInsight, MasterNodeIO, CryptoID,
                DashBlockExplorer
            ],
            'push_tx': [
                MasterNodeIO, DashOrgInsight, SiampmDashInsight, DashBlockExplorer
            ],
            'unspent_outputs': [
                MasterNodeIO, SiampmDashInsight, DashOrgInsight, CryptoID,
                DashBlockExplorer
            ],
            'get_block': [
                ProHashing, SiampmDashInsight, HolyTransaction, MasterNodeIO,
                DashOrgInsight, DashBlockExplorer
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
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'transaction_form': 'ppc-timestamp',
        'port': 45444,
        'last_pow_block': 260799,
        'seed_nodes': [
            'seed.reddcoin.com'
        ],
        'services': {
            'current_price': {
                'btc': [Bittrex, YoBit, BleuTrade, Cryptopia, NovaExchange],
                'ltc': [Cryptopia, NovaExchange], 'esp2': [NovaExchange],
                'doge': [Cryptopia, BleuTrade], 'uno': [Cryptopia], '*': [Cryptonator]
            },
            'address_balance': [ReddcoinCom, ProHashing],
            'historical_transactions': [ReddcoinCom, ProHashing],
            'single_transaction': [ReddcoinCom],
            'push_tx': [ReddcoinCom],
            'unspent_outputs': [ReddcoinCom],
            'get_block': [ReddcoinCom, ProHashing],
        },
    },

    'nmc': {
        'name': 'Namecoin',
        'address_version_byte': 52,
        'bip44_coin_type': 0x80000007,
        'private_key_prefix': 0x80,
        'genesis_date': datetime(2011, 4, 18),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [Poloniex, BleuTrade, YoBit, xBTCe, Cryptopia, Vircurex, LiveCoin],
                'ltc': [Cryptopia], 'usd': [xBTCe],
                'doge': [Cryptopia, BleuTrade], 'uno': [Cryptopia], '*': [Cryptonator]
            },
            'address_balance': [WebBTC, Bchain]
        }
    },
    'aur': {
        'name': 'Auroracoin',
        'address_version_byte': 23,
        'bip44_coin_type': 0x80000055,
        'private_key_prefix': 0x97,
        'genesis_date': datetime(2014, 2, 2),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [Bittrex, YoBit, Cryptopia], 'ltc': [Cryptopia],
                'doge': [Cryptopia], 'uno': [Cryptopia], '*': [Cryptonator]
            },
            'address_balance': [CryptoID, ProHashing],
            'historical_transactions': [ProHashing],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': []
        },
    },
    'emc': {
        'name': 'Emercoin',
        'address_version_byte': 33,
        'bip44_coin_type': None,
        'private_key_prefix': 128,
        'message_magic': b"\xe6\xe8\xe9\xe5",
        'genesis_date': datetime(2011, 11, 5),
        'github_link': "https://github.com/emercoin/emercoin",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [YoBit, HitBTC, Bittrex, xBTCe, Cryptopia, LiveCoin],
                'ltc': [Cryptopia], 'dash': [LiveCoin], 'eth': [LiveCoin],
                'usd': [xBTCe, LiveCoin], 'cny': [BTC38], 'rur': [LiveCoin],
                'xmr': [LiveCoin], 'doge': [Cryptopia], 'uno': [Cryptopia],
                '*': [Cryptonator]
            },
            'address_balance': [Mintr],
            'historical_transactions': [],
            'single_transaction': [Mintr],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [Mintr]
        },
    },

    'gsm': {
        'name': 'GSMcoin',
        'address_version_byte': 38,
        'bip44_coin_type': None,
        'private_key_prefix': 166,
        'genesis_date': datetime(1, 1, 1),
        'github_link': "https://github.com/gsmcoin/GSMcoin",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {'btc': [YoBit]},
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        },
    },

    'erc': {
        'name': 'Europecoin',
        'address_version_byte': 33,
        'bip44_coin_type': None,
        'private_key_prefix': 161,
        'genesis_date': datetime(1, 1, 1),
        'github_link': "https://github.com/EuropecoinEUORG/EuropecoinV2",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [Bittrex],
                '*': [Cryptonator],
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        },
    },

    'tx': {
        'name': 'TransferCoin',
        'address_version_byte': 66,
        'bip44_coin_type': None,
        'private_key_prefix': 153,
        'message_magic': b"\xd1\x2e\x1e\xe6",
        'genesis_date': datetime(1, 1, 1),
        'github_link': "https://github.com/transferdev/Transfercoin",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [Bittrex, YoBit, Cryptopia, LiveCoin], 'ltc': [Cryptopia],
                'doge': [Cryptopia], 'uno': [Cryptopia], '*': [Cryptonator]
            },
            'address_balance': [CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': []
        },
    },
    'maid': {
        'name': 'MaidSafeCoin',
        'address_version_byte': 0,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(1, 1, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [Bittrex, Poloniex, Cryptopia, HitBTC, LiveCoin], 'ltc': [Cryptopia],
                'usd': [HitBTC],
                'doge': [Cryptopia], 'uno': [Cryptopia], '*': [Cryptonator]
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        },
    },
    'tips': {
        'name': 'FedoraCoin',
        'address_version_byte': 33,
        'bip44_coin_type': None,
        'private_key_prefix': 161   ,
        'genesis_date': datetime(2013, 12, 21),
        'github_link': "https://github.com/fedoracoin/fedoracoin",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'ltc': [BTER, NovaExchange], 'moon': [NovaExchange],
                '*': [Cryptonator], 'piggy': [NovaExchange]
            },
            'address_balance': [CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': []
        },
    },
    'karma': {
        'name': 'KarmaCoin',
        'address_version_byte': 45,
        'bip44_coin_type': None,
        'private_key_prefix': 173,
        'genesis_date': datetime(2014, 2, 4),
        'github_link': "https://github.com/karmacoin-team/karmacoin",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [YoBit],
                '*': [Cryptonator],
            },
            'address_balance': [CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': []
        },
    },
    'flap': {
        'name': 'FlappyCoin',
        'address_version_byte': 35,
        'bip44_coin_type': None,
        'private_key_prefix': 163,
        'genesis_date': datetime(2014, 2, 14),
        'github_link': "https://github.com/flappycoin-project/flappycoin",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {},
            'address_balance': [CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': []
        },
    },
    'pot': {
        'name': 'PotCoin',
        'address_version_byte': 55,
        'bip44_coin_type': 0x80000051,
        'private_key_prefix': 183,
        'genesis_date': datetime(2014, 1, 21),
        'github_link': "https://github.com/potcoin/Potcoin",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 420,
            'minutes_per_block': 0.666666666,
            'full_cap': 420000000,
            'blocks_per_era': 210000
        },
        'services': {
            'current_price': {
                'btc': [Bittrex, Cryptopia, BleuTrade], 'ltc': [Cryptopia],
                'doge': [Cryptopia, BleuTrade], 'uno': [Cryptopia], '*': [Cryptonator],
            },
            'address_balance': [CryptoID, ProHashing],
            'historical_transactions': [ProHashing],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': [ProHashing]
        },
    },
    'bqc': {
        'name': 'BBQcoin',
        'address_version_byte': 85,
        'bip44_coin_type': None,
        'private_key_prefix': 213,
        'genesis_date': datetime(2012, 7, 15),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                '*': [Cryptonator],
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        },
    },
    'nvc': {
        'name': 'Novacoin',
        'address_version_byte': 8,
        'bip44_coin_type': 0x80000032,
        'private_key_prefix': 136,
        'genesis_date': datetime(2012, 10, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [YoBit, Cryptopia, BleuTrade, LiveCoin], 'ltc': [Cryptopia],
                'doge': [Cryptopia, BleuTrade], '*': [Cryptonator],
            },
            'address_balance': [CryptapUS, Bchain],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        },
    },
    'uno': {
        'name': 'Unobtanium',
        'address_version_byte': 130,
        'bip44_coin_type': 0x8000005c,
        'private_key_prefix': 224,
        'genesis_date': datetime(2013, 10, 17),
        'header_hash_algo': 'double-sha256',
        'port': None,
        'supply_data': {
            'method': 'standard',
            'full_cap': 250000,
            'blocks_per_era': 100000,
            'minutes_per_block': 3,
        },
        'services': {
            'current_price': {
                'btc': [Bittrex, CCex, Cryptopia, BleuTrade], 'ltc': [Cryptopia],
                'usd': [CCex, Cryptopia], 'doge': [Cryptopia, BleuTrade],
                '*': [Cryptonator],
            },
            'address_balance': [UNOCryptap, CryptoID],
            'historical_transactions': [UNOCryptap, CryptoID],
            'single_transaction': [UNOCryptap],
            'push_tx': [UNOCryptap],
            'unspent_outputs': [UNOCryptap, CryptoID],
            'get_block': [UNOCryptap]
        },
    },
    'ric': {
        'name': 'Riecoin',
        'address_version_byte': 60,
        'bip44_coin_type': 0x8000008f,
        'private_key_prefix': 128,
        'genesis_date': datetime(2014, 2, 11, 0, 49, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 50,
            'minutes_per_block': 2.5,
            'blocks_per_era': 840000,
        },
        'services': {
            'current_price': {
                'btc': [Poloniex], 'cny': [BTC38],
                '*': [Cryptonator],
            },
            'address_balance': [RICCryptap, Bchain, CryptoID],
            'historical_transactions': [RICCryptap],
            'single_transaction': [RICCryptap, CryptoID],
            'push_tx': [RICCryptap],
            'unspent_outputs': [RICCryptap, CryptoID],
            'get_block': [RICCryptap]
        },
    },
    'xrp': {
        'name': 'Ripple',
        'genesis_date': datetime(2011, 3, 1),
        'bip44_coin_type': 0x80000090,
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [
                    Bittrex, Bitstamp, Poloniex, BitFinex, CoinEgg,
                    HitBTC, Bitso, BitcoinIndonesia, Kraken, ZB
                ],
                'cad': [Kraken], 'usd': [BitFinex, Bitstamp, Kraken, xBTCe, ZB],
                'eur': [Bitstamp, Kraken, xBTCe], 'jpy': [Kraken, BitBank], 'mxn': [Bitso],
                'krw': [CoinOne], 'cny': [BTC38], '*': [Cryptonator], 'qc': [ZB],
            },
        }
    },
    'thc': {
        'name': 'HempCoin',
        'address_version_byte': 40,
        'bip44_coin_type': None,
        'private_key_prefix': 168,
        'genesis_date': datetime(1, 1, 1),
        'github_link': "https://github.com/hempcoin-project/THC",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': 1.0,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [Bittrex], '*': [Cryptonator],
            },
            'address_balance': [THCBlock, BlockExperts],
            'historical_transactions': [],
            'single_transaction': [THCBlock, BlockExperts],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [THCBlock, BlockExperts]
        },
    },
    'dope': {
        'name': 'Dopecoin',
        'address_version_byte': 8,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'genesis_date': datetime(1, 1, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [Bittrex, Cryptonator],
                '*': [Cryptonator],
            },
            'address_balance': [BlockExperts],
            'historical_transactions': [],
            'single_transaction': [BlockExperts],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [BlockExperts]
        },
    },
    'dime': {
        'name': 'Dimecoin',
        'address_version_byte': 15,
        'bip44_coin_type': None,
        'script_hash_byte': 9,
        'private_key_prefix': 143,
        'genesis_date': datetime(2014, 12, 23),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'seed_nodes': [
            'dime.mine-pool.net:11931',
            '209.126.65.116:11931',
            '122.10.88.44:11931',
        ],
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': 1.066666667,
            'full_cap': 528000000,
            'blocks_per_era': 512000,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [YoBit, LiveCoin], 'doge': [Cryptopia], 'rur': [LiveCoin],
                'ltc': [Cryptopia], 'uno': [Cryptopia], 'eur': [LiveCoin],
                '*': [Cryptonator],
            },
            'address_balance': [BlockExperts, CryptoID],
            'historical_transactions': [],
            'single_transaction': [BlockExperts, CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': [BlockExperts]
        },
    },
    'xcp': {
        'name': 'CounterParty',
        'address_version_byte': 0,
        'bip44_coin_type': 0x80000009,
        'private_key_prefix': 128,
        'genesis_date': datetime(2014, 1, 2),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [Bittrex, Poloniex, Cryptonator],
                '*': [Cryptonator],
            },
            'address_balance': [CoinDaddy1, CoinDaddy2, CounterPartyChain],
            'historical_transactions': [CoinDaddy1, CoinDaddy2],
            'single_transaction': [CoinDaddy1, CoinDaddy2],
            'push_tx': [CoinDaddy1, CoinDaddy2],
            'unspent_outputs': [CoinDaddy1],
            'get_block': [CoinDaddy1, CoinDaddy2]
        },
    },
    'eth': {
        'name': 'Ethereum',
        'address_form': "eth-0xhex",
        'private_key_form': "eth-pkhex",
        'transaction_form': 'eth',
        'bip44_coin_type': 0x8000003c,
        'genesis_date': datetime(2015, 7, 30),
        'port': None,
        'supply_data': {
            'instamine': 72009990.50
        },
        'services': {
            'current_price': {
                'rur': [YoBit, xBTCe, LiveCoin], 'cny': [ViaBTC, Yunbi, xBTCe],
                'usd': [
                    GDAX, Kraken, BitFinex, HitBTC, BitZ, OKEX, xBTCe, Liqui,
                    LiveCoin, KuCoin, ZB, EXX, Bibox
                ],
                'jpy': [Kraken, xBTCe], 'cad': [Kraken],  'krw': [CoinOne, CoinNest],
                'eur': [xBTCe, Kraken, HitBTC], 'gbp': [Kraken], 'mxn': [Bitso],
                'btc': [
                    Poloniex, GDAX, BitFinex, Kraken, xBTCe, BleuTrade, Bittrex,
                    CexIO, HitBTC, BitcoinIndonesia, EtherChain, YoBit, Cryptopia,
                    Bitso, Liqui, LiveCoin, BitFlyer, KuCoin, CCex, OKEX, BitZ, ZB,
                    BitBank, EXX, Bibox
                ],
                'ltc': [Cryptopia, xBTCe], 'doge': [Cryptopia, BleuTrade], 'uno': [Cryptopia],
                '*': [Cryptonator],
            },
            'address_balance': [Etherscan, EtherChain, ETCchain, EthPlorer],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        },
    },
    'etc': {
        'name': 'Ethereum Classic',
        'address_form': "eth-0xhex",
        'private_key_form': "eth-pkhex",
        'transaction_form': 'eth',
        'bip44_coin_type': 0x8000003d,
        'genesis_date': datetime(2016, 7, 20),
        'port': None,
        'services': {
            'current_price': {
                'btc': [
                    Poloniex, BitFinex, HitBTC, Bittrex, CCex, CoinEgg,
                    Kraken, Cryptopia, YoBit, Yunbi, OKEX, BitZ, ZB, EXX
                ],
                'usd': [Kraken, BitFinex, OKEX, CCex, HitBTC, ZB, EXX], 'doge': [Cryptopia],
                'ltc': [CCex, Cryptopia], 'uno': [Cryptopia], 'krw': [CoinOne, CoinNest],
                '*': [Cryptonator], 'eth': [Kraken, HitBTC, OKEX, EXX], 'eur': [Kraken],
                'qc': [EXX], 'hsr': [EXX]
            },
            'address_balance': [ETCchain],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        },
    },
    'xmr': {
        'name': 'Monero',
        'address_version_byte': None,
        'bip44_coin_type': 0x80000080,
        'private_key_prefix': None,
        'genesis_date': datetime(2014, 4, 18),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [
                    Poloniex, Bittrex, BitFinex, HitBTC,
                    Kraken, Cryptopia, LiveCoin
                ],
                'usd': [BitFinex, HitBTC, Kraken, Cryptopia, LiveCoin],
                'ltc': [Cryptopia], 'doge': [Cryptopia], 'uno': [Cryptopia],
                'nzd': [Cryptopia], 'eur': [Kraken], 'eth': [HitBTC],
                '*': [Cryptonator],
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        }
    },
    'blk': {
        'name': 'Blackcoin',
        'message_magic': b"\x70\x35\x22\x05",
        'address_version_byte': 25,
        'bip44_coin_type': 0x8000000a,
        'private_key_prefix': 153,
        'genesis_date': datetime(1, 1, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [Poloniex, Cryptopia, BitZ, UseCryptos, BleuTrade, LiveCoin, CoinEgg],
                'ltc': [Cryptopia], 'doge': [Cryptopia, BleuTrade], 'uno': [Cryptopia],
                '*': [Cryptonator], 'cny': [BTC38],
            },
            'address_balance': [
                CryptoID, HolyTransaction, Bchain
            ],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        },
    },
    'xpm': {
        'name': 'Primecoin',
        'address_version_byte': 23,
        'bip44_coin_type': 0x80000018,
        'private_key_prefix': 151,
        'genesis_date': datetime(1, 1, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'btc': [Poloniex, BitZ, Cryptopia, Vircurex, BleuTrade, CoinEgg],
                'ltc': [Cryptopia], 'doge': [Cryptopia, BleuTrade],
                'uno': [Cryptopia], 'cny': [BTC38], '*': [Cryptonator],
            },
            'address_balance': [
                Bchain
            ],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        },
    },
    'pivx': {
        'name': 'PivX',
        'address_version_byte': 30,
        'bip44_coin_type': 0x80000077,
        'private_key_prefix': 212,
        'script_hash_byte': 0xD,
        'message_magic': b"\x90\xc4\xfd\xe9",
        'genesis_date': datetime(1, 1, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': 51472,
        'seed_nodes': [
            'pivx.seed.fuzzbawls.pw',
            'pivx.seed2.fuzzbawls.pw',
            'coin-server.com',
            's3v3nh4cks.ddns.net'
        ],
        'services': {
            'current_price': {
                'btc': [Bittrex, Cryptopia, YoBit, LiveCoin],
                'ltc': [Cryptopia], 'doge': [Cryptopia], 'uno': [Cryptopia],
                '*': [Cryptonator], 'eth': [LiveCoin], 'eur': [LiveCoin],
                'rur': [LiveCoin], 'xmr': [LiveCoin], 'usd': [Cryptopia, LiveCoin],
            },
            'address_balance': [PressTab, CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': []
        },
    },
    'zec': {
        'name': 'ZCash',
        'address_version_byte': 7352,
        'bip44_coin_type': 0x80000085,
        'private_key_prefix': 128,
        'script_hash_byte': 0x1cbd,
        'genesis_date': datetime(2016, 10, 28, 7, 56),
        'message_magic': b"\x24\xe9\x27\x64",
        'github_link': "https://github.com/zcash/zcash",
        'header_hash_algo': 'double-sha256',
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': 8233,
        'services': {
            'current_price': {
                'btc': [Bittrex, BitFinex, HitBTC, YoBit, Kraken, BitZ],
                'usd': [BitFinex, Kraken, HitBTC], 'bch': [CoinEx],
                'eth': [HitBTC], 'eur': [Kraken], 'cny': [ViaBTC], '*': [Cryptonator],
            },
            'address_balance': [ZChain, MercerWeiss],
            'historical_transactions': [MercerWeiss],
            'single_transaction': [MercerWeiss],
            'push_tx': [MercerWeiss],
            'unspent_outputs': [MercerWeiss],
            'get_block': [MercerWeiss]
        },
    },
    'grs': {
        'name': 'Groestlcoin',
        'address_version_byte': 36,
        'bip44_coin_type': 0x80000011,
        'private_key_prefix': 128,
        'script_hash_byte': 0x05,
        'message_magic': b"\xF9\xBE\xB4\xD4",
        'genesis_date': datetime(2014, 3, 20, 19, 13, 49),
        'header_hash_algo': 'groestl',
        'transaction_hash_algo': 'single-sha256',
        'script_hash_algo': 'groestl',
        'address_form': 'groestl-check',
        'github_link': 'https://github.com/Groestlcoin/groestlcoin',
        'port': 1331,
        'seed_nodes': [
            'groestlcoin.org',
            'jswallet.groestlcoin.org',
            'electrum1.groestlcoin.org',
            'electrum2.groestlcoin.org'
        ],
        'services': {
            'current_price': {
                'btc': [Bittrex],
                '*': [Cryptonator],
            },
            'address_balance': [CryptoID, Groestlsight],
            'historical_transactions': [Groestlsight],
            'single_transaction': [CryptoID, Groestlsight],
            'push_tx': [Groestlsight],
            'unspent_outputs': [CryptoID, Groestlsight],
            'get_block': [Groestlsight]
        },
    },
    'sys': {
        'name': 'Syscoin 2.1',
        'address_version_byte': 0,
        'bip44_coin_type': 0x80000039,
        'private_key_prefix': 128,
        'script_hash_byte': 5,
        'genesis_date': datetime(1, 1, 1),
        'header_hash_algo': 'double-sha256',
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        'github_link': "https://github.com/syscoin/syscoin2",
        'services': {
            'current_price': {
                'btc': [Bittrex, YoBit, BTC38, LiveCoin],
                '*': [Cryptonator],
            },
            'address_balance': [ProHashing, CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': []
        },
    },
    'bun': {
        'name': 'BunnyCoin',
        'address_version_byte': 26,
        'bip44_coin_type': None,
        'private_key_prefix': 154,
        'script_hash_byte': 22,
        'genesis_date': datetime(2014, 4, 25, 16, 0),
        'header_hash_algo': 'scrypt',
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'services': {
            'current_price': {
                'ltc': [Cryptopia, NovaExchange], 'moon': [NovaExchange],
                'doge': [Cryptopia, NovaExchange], 'uno': [Cryptopia],
            },
            'address_balance': [ProHashing, CryptoChat],
            'historical_transactions': [CryptoChat],
            'single_transaction': [CryptoChat],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [CryptoChat]
        },
    },
    'bvc': {
        'name': 'BeaverCoin',
        'address_version_byte': 25,
        'bip44_coin_type': None,
        'private_key_prefix': 176,
        'genesis_date': datetime(1, 1, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 8,
            'minutes_per_block': 1,
            'full_cap': 3360000,
            'blocks_per_era': 210000,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [Cryptopia], 'ltc': [Cryptopia], 'doge': [Cryptopia],
                'uno': [Cryptopia],
            },
            'address_balance': [ProHashing, BeavercoinBlockchain],
            'historical_transactions': [BeavercoinBlockchain],
            'single_transaction': [BeavercoinBlockchain],
            'push_tx': [BeavercoinBlockchain],
            'unspent_outputs': [BeavercoinBlockchain],
            'get_block': [BeavercoinBlockchain]
        },
    },
    'cat': {
        'name': 'Catcoin',
        'address_version_byte': 21,
        'bip44_coin_type': None,
        'private_key_prefix': 149,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 50,
            'minutes_per_block': 10,
            'full_cap': 21000000,
            'blocks_per_era': 210000,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {},
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        },
    },
    'lemon': {
        'name': 'LemonCoin',
        'address_version_byte': 48,
        'bip44_coin_type': None,
        'private_key_prefix': 176,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 20,
            'minutes_per_block': 1,
            'full_cap': 31000000,
            'blocks_per_era': 525000,
            'reward_ends_at_block': None,
            'ico': 10000000,
            'ico_burn': 8960948,
        },
        'services': {
            'current_price': {
                'btc': [Cryptopia], 'ltc': [Cryptopia], 'doge': [Cryptopia],
                'uno': [Cryptopia],
            },
            'address_balance': [LemoncoinOfficial],
            'historical_transactions': [LemoncoinOfficial],
            'single_transaction': [LemoncoinOfficial],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [LemoncoinOfficial]
        },
    },
    'geert': {
        'name': 'Geertcoin',
        'address_version_byte': 38,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'message_magic': None,
        'genesis_date': datetime(2017, 2, 12, 6, 25, 23),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 200,
            'minutes_per_block': 2.5,
            'full_cap': None,
            'blocks_per_era': 24000,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [Cryptopia], 'ltc': [Cryptopia], 'doge': [Cryptopia]
            },
            'address_balance': [GeertcoinExplorer],
            'historical_transactions': [GeertcoinExplorer],
            'single_transaction': [GeertcoinExplorer],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [GeertcoinExplorer]
        },
    },
    'ulm': {
        'name': 'UnlimitedCoin',
        'address_version_byte': 68,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'message_magic': None,
        'genesis_date': datetime(2017, 5, 19, 17, 55, 39),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {'btc': [NovaExchange]},
            'address_balance': [UnlimitedCoinOfficial],
            'historical_transactions': [UnlimitedCoinOfficial],
            'single_transaction': [UnlimitedCoinOfficial],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [UnlimitedCoinOfficial]
        },
    },
    'mars': {
        'name': 'MarsCoin',
        'address_version_byte': 50,
        'bip44_coin_type': 0x8000006b,
        'private_key_prefix': 178,
        'script_hash_byte': 5,
        'message_magic': None,
        'genesis_date': datetime(2014, 1, 1, 15, 37, 7),
        'header_hash_algo': 'scrypt',
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 50,
            'minutes_per_block': 2.05,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {'btc': [NovaExchange], 'ltc': [NovaExchange]},
            'address_balance': [MarscoinOfficial],
            'historical_transactions': [MarscoinOfficial],
            'single_transaction': [MarscoinOfficial],
            'push_tx': [MarscoinOfficial],
            'unspent_outputs': [MarscoinOfficial],
            'get_block': [MarscoinOfficial]
        },
    },
    'moon': {
        'name': 'Mooncoin',
        'address_version_byte': 3,
        'bip44_coin_type': None,
        'private_key_prefix': 131,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': 1.5,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [CCex, NovaExchange, BleuTrade], 'usd': [CCex],
                'ltc': [CCex, NovaExchange, BleuTrade], 'doge': [CCex]
            },
            'address_balance': [ProHashing, Bchain],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        },
    },
    'rby': {
        'name': 'Rubycoin',
        'address_version_byte': 60,
        'bip44_coin_type': 0x80000010,
        'private_key_prefix': 188,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': 1.5,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [Bittrex, Cryptopia], 'ltc': [Cryptopia],
                'doge': [Cryptopia], 'uno': [Cryptopia]
            },
            'address_balance': [CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': []
        },
    },
    'pnd': {
        'name': 'PandaCoin',
        'address_version_byte': 55,
        'bip44_coin_type': 0x80000025,
        'private_key_prefix': 183,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': 1.0,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [YoBit], 'ltc': [Cryptopia],
                'doge': [Cryptopia], 'uno': [Cryptopia]
            },
            'address_balance': [CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': []
        },
    },
    'trc': {
        'name': 'TerraCoin',
        'address_version_byte': 0,
        'bip44_coin_type': 0x80000053,
        'private_key_prefix': 128,
        'message_magic': b"\x42\xba\xbe\x56",
        'genesis_date': datetime(1, 1, 1),
        'github_link': "https://github.com/clockuniverse/terracoin",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 20,
            'minutes_per_block': 2,
            'full_cap': None,
            'blocks_per_era': 1050000,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [CCex, Vircurex, Cryptopia], 'usd': [CCex, Vircurex],
                'ltc': [CCex, Cryptopia, NovaExchange],
                'doge': [CCex, Cryptopia, NovaExchange]
            },
            'address_balance': [TerracoinIO, Bchain],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': []
        },
    },
    'dgc': {
        'name': 'DigitalCoin',
        'address_version_byte': 30,
        'bip44_coin_type': 0x80000012,
        'private_key_prefix': 158,
        'message_magic': b"\xfb\xc0\xb6\xdb",
        'genesis_date': datetime(1, 1, 1),
        'github_link': "https://github.com/DGCDev/digitalcoin",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': 0.666666666,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [BleuTrade, NovaExchange, Cryptopia, Vircurex],
                'usd': [Vircurex], 'eur': [Vircurex], 'cny': [BTC38],
                'ltc': [Cryptopia, NovaExchange, Vircurex],
                'doge': [Vircurex, BleuTrade, Cryptopia, NovaExchange]
            },
            'address_balance': [CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': []
        },
    },
    'qrk': {
        'name': 'Quark',
        'address_version_byte': 58,
        'bip44_coin_type': None,
        'private_key_prefix': 186,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [NovaExchange, Vircurex, Cryptopia, BTC38],
                'ltc': [Vircurex, NovaExchange, Cryptopia], 'eur': [Vircurex],
                'usd': [Vircurex], 'doge': [Cryptopia, NovaExchange],
            },
            'address_balance': [CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': []
        },
    },
    'tse': {
        'name': 'Tattoocoin',
        'address_version_byte': 65,
        'bip44_coin_type': None,
        'private_key_prefix': 193,
        'message_magic': None,
        'genesis_date': datetime(2016, 12, 29, 21, 53, 10),
        'github_link': 'https://github.com/CryptoCoderz/Tattoocoin-TSE',
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [YoBit, CCex, NovaExchange, Cryptopia],
                'ltc': [CCex, NovaExchange, Cryptopia], 'usd': [CCex],
                'doge': [CCex, Cryptopia],
            },
            'address_balance': [CryptoChat],
            'historical_transactions': [CryptoChat],
            'single_transaction': [CryptoChat],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [CryptoChat]
        },
    },
    'xvg': {
        'name': 'Verge',
        'address_version_byte': 30,
        'bip44_coin_type': 0x8000004d,
        'private_key_prefix': 158,
        'message_magic': None,
        'genesis_date': datetime(2014, 10, 9, 18, 22, 44),
        'github_link': "https://github.com/vergecurrency/VERGE",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': 0.5,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [YoBit, CCex, Bittrex, Cryptopia, NovaExchange],
                'ltc': [CCex, Cryptopia, NovaExchange], 'usd': [CCex],
                'doge': [CCex, NovaExchange, Cryptopia]
            },
            'address_balance': [VergeCurrencyInfo, ProHashing],
            'historical_transactions': [VergeCurrencyInfo],
            'single_transaction': [VergeCurrencyInfo],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [VergeCurrencyInfo]
        },
    },
    '1337': {
        'name': '1337',
        'address_version_byte': 48,
        'bip44_coin_type': None,
        'private_key_prefix': 176,
        'script_hash_byte': 28,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': 'https://github.com/Velvet78/1337',
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [YoBit, Cryptopia, NovaExchange],
                'ltc': [Cryptopia, NovaExchange], 'moon': [NovaExchange],
                'doge': [Cryptopia, NovaExchange],
            },
            'address_balance': [CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': [],
            "get_optimal_fee": []
        },
    },
    'cj': {
        'name': 'CryptoJacks',
        'address_version_byte': 28,
        'bip44_coin_type': None,
        'private_key_prefix': 156,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': "https://github.com/cryptojacks/CryptoJacks",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [CCex, NovaExchange, Cryptopia, YoBit],
                'ltc': [CCex, NovaExchange, Cryptopia], 'usd': [CCex],
                'doge': [Cryptopia, NovaExchange]
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [],
            "get_optimal_fee": []
        },
    },
    'fjc': {
        'name': 'FujiCoin',
        'address_version_byte': 36,
        'bip44_coin_type': 0x8000004b,
        'private_key_prefix': 164,
        'script_hash_byte': 16,
        'message_magic': b"\x66\x75\x6a\x69",
        'genesis_date': datetime(2014, 6, 27, 23, 0),
        'github_link': "https://github.com/fujicoin/fujicoin",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': 3777,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': 1,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [YoBit, CCex, NovaExchange, Cryptopia, BleuTrade],
                'ltc': [CCex, Cryptopia, NovaExchange], 'usd': [CCex],
                'doge': [CCex, NovaExchange, Cryptopia]
            },
            'address_balance': [FujiInsght],
            'historical_transactions': [FujiInsght],
            'single_transaction': [FujiInsght],
            'push_tx': [FujiInsght],
            'unspent_outputs': [FujiInsght],
            'get_block': [FujiInsght],
            "get_optimal_fee": []
        },
    },
    'note': {
        'name': 'DNotes',
        'address_version_byte': 31,
        'bip44_coin_type': None,
        'private_key_prefix': 159,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': "https://github.com/DNotesCoin/DNotes/",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': 1,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [YoBit, CCex, Poloniex, NovaExchange, Cryptopia],
                'ltc': [CCex, Cryptopia, NovaExchange], 'usd': [CCex],
                'doge': [CCex, NovaExchange, Cryptopia]
            },
            'address_balance': [CryptoID, ProHashing],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': [],
            "get_optimal_fee": []
        },
    },
    'song': {
        'name': 'SongCoin',
        'address_version_byte': 63,
        'bip44_coin_type': None,
        'private_key_prefix': 191,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': "https://github.com/Songcoin/Songcoin",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': 2,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [YoBit, CCex, NovaExchange, Cryptopia],
                'ltc': [CCex, Cryptopia], 'usd': [CCex],
                'doge': [CCex, NovaExchange, Cryptopia]
            },
            'address_balance': [ProHashing],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'ptc': {
        'name': 'Pesetacoin',
        'address_version_byte': 47,
        'bip44_coin_type': 0x8000006d,
        'private_key_prefix': 175,
        'message_magic': b"\xc0\xc0\xc0\xc0",
        'genesis_date': datetime(2013, 12, 31, 22, 23, 8),
        'github_link': "https://github.com/pesetachain/pesetacoin-0.9",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'per_era',
            'eras': [
                {'start': 0,      'end': 525600, 'reward': 166.386},
                {'start': 525601, 'end': 550000, 'reward': 83.193},
                {'start': 550001, 'end': 1051200, 'reward': 50},
                {'start': 1051201, 'end': 1576800, 'reward': 25},
                {'start': 1576801, 'end': 2628000, 'reward': 10},
                {'start': 2628001, 'end': 8409600, 'reward': 5},
                {'start': 8409601, 'end': None, 'reward': 0},
            ],
            'full_cap': 166386000,
            'reward_ends_at_block': 8409601
        },
        'services': {
            'current_price': {
                'btc': [Bittrex, Cryptopia, NovaExchange], 'ltc': [Cryptopia],
                'uno': [Cryptopia], 'doge': [Cryptopia]
            },
            'address_balance': [PesetacoinInfo, CryptoID, PresetacoinInsight],
            'historical_transactions': [PesetacoinInfo, PresetacoinInsight],
            'single_transaction': [PesetacoinInfo, CryptoID, PresetacoinInsight],
            'push_tx': [PresetacoinInsight],
            'unspent_outputs': [PesetacoinInfo, CryptoID, PresetacoinInsight],
            'get_block': [PesetacoinInfo],
            'get_optimal_fee': []
        },
    },
    'tes': {
        'name': 'TeslaCoin',
        'address_version_byte': 11,
        'bip44_coin_type': None,
        'private_key_prefix': 139,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': "https://github.com/TeslacoinFoundation/Teslacoin",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [YoBit, Cryptopia, NovaExchange], 'ltc': [Cryptopia, NovaExchange],
                'uno': [Cryptopia], 'doge': [Cryptopia, NovaExchange]
            },
            'address_balance': [CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'xvc': {
        'name': 'Vcash',
        'address_version_byte': 71,
        'bip44_coin_type': None,
        'private_key_prefix': 199,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': "https://github.com/openvcash/vcash",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [Bittrex, Poloniex]
            },
            'address_balance': [VChainInfo],
            'historical_transactions': [],
            'single_transaction': [VChainInfo],
            'push_tx': [],
            'unspent_outputs': [VChainInfo],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'meow': {
        'name': 'KittehCoin',
        'address_version_byte': 45,
        'bip44_coin_type': None,
        'private_key_prefix': 173,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': "https://github.com/kittehcoin/kittehcoin",
        'header_hash_algo': 'scrypt',
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': 1.0,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'ltc': [Cryptopia, NovaExchange], 'doge': [Cryptopia]
            },
            'address_balance': [ProHashing, CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'huc': {
        'name': 'HunterCoin',
        'address_version_byte': 40,
        'bip44_coin_type': None,
        'private_key_prefix': 168,
        'message_magic': b"\xf9\xbe\xb4\xfe",
        'genesis_date': datetime(1, 1, 1),
        'github_link': "https://github.com/chronokings/huntercore",
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': 1.0,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [Poloniex], 'ltc': [], 'usd': [], 'doge': []
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'bcc': {
        'name': 'BitConnect',
        'address_version_byte': 18,
        'bip44_coin_type': None,
        'private_key_prefix': 146,
        'script_hash_byte': 85,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': None,
        'header_hash_algo': None,
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [NovaExchange, LiveCoin], 'ltc': [], 'usd': [], 'doge': [NovaExchange]
            },
            'address_balance': [CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'dmd': {
        'name': 'Diamond',
        'address_version_byte': 90,
        'bip44_coin_type': None,
        'private_key_prefix': 218,
        'script_hash_byte': 8,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': 'https://github.com/DMDcoin/Diamond',
        'header_hash_algo': "groestl",
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [Bittrex], 'ltc': [], 'usd': [], 'doge': []
            },
            'address_balance': [CryptoID],
            'historical_transactions': [],
            'single_transaction': [CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'nlc2': {
        'name': 'NoLimitCoin',
        'address_version_byte': 53,
        'bip44_coin_type': None,
        'private_key_prefix': 181,
        'script_hash_byte': 92,
        'message_magic': None,
        'genesis_date': datetime(2016, 5, 28, 20, 15),
        'github_link': 'https://github.com/NoLimitCoin/NoLimitCoin',
        'header_hash_algo': None,
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': 2,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [], 'ltc': [], 'usd': [], 'doge': []
            },
            'address_balance': [NoLimitCoinIquidus],
            'historical_transactions': [],
            'single_transaction': [NoLimitCoinIquidus],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [NoLimitCoinIquidus],
            'get_optimal_fee': []
        },
    },
    'cloak': {
        'name': 'CloakCoin',
        'address_version_byte': 27,
        'bip44_coin_type': None,
        'private_key_prefix': 155,
        'script_hash_byte': 85,
        'message_magic': None,
        'genesis_date': datetime(2014, 5, 31, 11, 52, 35),
        "github_link": "https://github.com/cashmen/CloakCoinRelaunch",
        'header_hash_algo': None,
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [LiveCoin, Bittrex, Cryptopia, YoBit, CryptoDao], 'ltc': [Cryptopia],
                'usd': [LiveCoin], 'doge': [Cryptopia]
            },
            'address_balance': [CloakCoinIquidus, CryptoID],
            'historical_transactions': [],
            'single_transaction': [CloakCoinIquidus, CryptoID],
            'push_tx': [],
            'unspent_outputs': [CryptoID],
            'get_block': [CloakCoinIquidus],
            'get_optimal_fee': []
        },
    },
    'mgc': {
        'name': 'MergeCoin',
        'address_version_byte': 50,
        'bip44_coin_type': 0x8000007c,
        'private_key_prefix': 178,
        'script_hash_byte': 5,
        'message_magic': b"\xc8\xe1\xd5\xec",
        'genesis_date': datetime(2017, 3, 23, 9, 23, 36),
        "github_link": "https://github.com/mergecoin-project/Mergecoin-master",
        'header_hash_algo': None,
        "transaction_form": "ppc-timestamp",
        'port': None,
        'seeds': [
            "47.89.43.73", "43.241.232.45", "47.89.178.249", "120.55.82.131",
            "121.41.19.30", "120.26.231.61", "47.94.89.212", "mergechain.com",
            "mergecoin.com"
        ],
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [CryptoDao], 'ltc': [], 'usd': [],
                'doge': [], 'cny': [BTC38]
            },
            'address_balance': [MergeCoinInsight],
            'historical_transactions': [MergeCoinInsight],
            'single_transaction': [MergeCoinInsight],
            'push_tx': [MergeCoinInsight],
            'unspent_outputs': [MergeCoinInsight],
            'get_block': [MergeCoinInsight],
            'get_optimal_fee': []
        },
    },
    'part': {
        'name': 'Particl',
        'address_version_byte': 56,
        'bip44_coin_type': 0x8000002c,
        'private_key_prefix': 108,
        'script_hash_byte': 60,
        'message_magic': b"\xfb\xf2\xef\xb4",
        'genesis_date': datetime(2017, 7, 17, 13, 0),
        'github_link': 'https://github.com/particl/particl-core',
        'header_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [Bittrex, BitZ], 'ltc': [], 'usd': [], 'doge': []
            },
            'address_balance': [CryptoID, ParticlInsight],
            'historical_transactions': [ParticlInsight],
            'single_transaction': [CryptoID, ParticlInsight],
            'push_tx': [ParticlInsight],
            'unspent_outputs': [CryptoID, ParticlInsight],
            'get_block': [ParticlInsight],
            'get_optimal_fee': []
        },
    },
    'bch': {
        'name': 'Bitcoin Cash',
        'forked_from': ('btc', 478559),
        'address_version_byte': 0,
        'message_magic': b"\xf9\xbe\xb4\xd9",
        'bip44_coin_type': 0x80000091,
        'private_key_prefix': 128,
        'script_hash_byte': 0x05,
        'genesis_date': datetime(2009, 1, 3, 18, 15, 5),
        'transaction_form': 'btc-cash-anti-replay',
        'header_hash_algo': 'double-sha256',
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'github_link': "https://github.com/Bitcoin-ABC/bitcoin-abc",
        'port': 8333,
        'seed_nodes': [
            "seed-abc.bitcoinforks.org",
            "seed.bitcoinabc.org",
            "btccash-seeder.bitcoinunlimited.info",
            "seed.bitprim.org",
            "seed.deadalnix.me",
            "seeder.criptolayer.net"
        ],
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 50,
            'minutes_per_block': 10,
            'full_cap': 21000000,
            'blocks_per_era': 210000,
            'reward_ends_at_block': 6930000
        },
        'services': {
            'current_price': {
                'btc': [
                    Bitstamp, Kraken, Bittrex, HitBTC, OKEX, BitZ,
                    CoinEgg, ZB, BitBank, EXX, Bibox
                ],
                'eur': [Kraken], 'usd': [HitBTC, Bitstamp, Kraken, OKEX, ZB], 'jpy': [BitBank],
                'eth': [HitBTC, Bibox], 'krw': [CoinNest], '*': [Cryptonator]
            },
            'address_balance': [
                BitpayInsightBCH, TrezorBCH, BlockExplorerCash, BlockDozer,
                BitcoinComCashExplorer, BCCBlock
            ],
            'historical_transactions': [
                BitcoinComCashExplorer, BitpayInsightBCH, TrezorBCH, BlockExplorerCash,
                BlockDozer, BCCBlock
            ],
            'single_transaction': [
                BCCBlock, BlockDozer, BitcoinComCashExplorer, BitpayInsightBCH, TrezorBCH,
                BlockExplorerCash
            ],
            'push_tx': [
                TrezorBCH, BlockExplorerCash, BitcoinComCashExplorer,
                BitpayInsightBCH, BlockDozer, BCCBlock
            ],
            'unspent_outputs': [
                BlockDozer, TrezorBCH, BlockExplorerCash, BitcoinComCashExplorer,
                BitpayInsightBCH, BCCBlock
            ],
            'get_block': [
                BitpayInsightBCH, BitcoinComCashExplorer, BCCBlock, BlockDozer,
                TrezorBCH, BlockExplorerCash
            ],
            "get_optimal_fee": []
        },
    },
    'leo': {
        'name': 'LEOcoin',
        'address_version_byte': 18,
        'bip44_coin_type': 0x8000007f,
        'private_key_prefix': 144,
        'script_hash_byte': 88,
        'message_magic': b"\x64\x6e\x78\x82",
        'genesis_date': datetime(2017, 5, 6, 11, 35, 28),
        "github_link": "https://github.com/Leocoin-project/LEOcoin",
        'header_hash_algo': None,
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        "seed_nodes": [
            "dnsseed.leocoin.org",
            "leoseed.leocoin.org",
        ] + ["node%s.leocoin.org" % x for x in range(1, 11)],
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [LiveCoin, BitZ], 'ltc': [], 'usd': [CCex, LiveCoin], 'doge': []
            },
            'address_balance': [LeoCoinInsight],
            'historical_transactions': [LeoCoinInsight],
            'single_transaction': [LeoCoinInsight],
            'push_tx': [LeoCoinInsight],
            'unspent_outputs': [LeoCoinInsight],
            'get_block': [LeoCoinInsight],
            'get_optimal_fee': []
        },
    },
    'game': {
        'name': 'GameCredits',
        'address_version_byte': 38,
        'bip44_coin_type': 0x80000065,
        'private_key_prefix': 166,
        'script_hash_byte': 5,
        'message_magic': b"\xfb\xc0\xb6\xdb",
        'genesis_date': datetime(1, 1, 1),
        "github_link": "https://github.com/gamecredits-project/GameCredits",
        'header_hash_algo': None,
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        "seed_nodes": [
            "dns.gmcseed1.acidpool.com",
            "dns.gmcseed2.version2.org",
            "gmc.cryptocloudhosting.org",
            "gmcnode1.version2.org"
        ],
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [
                    Poloniex, Bittrex, LiveCoin, Cryptopia, YoBit, NovaExchange,
                    BitZ, CoinEgg
                ], 'ltc': [Cryptopia], 'usd': [], 'doge': [Cryptopia, NovaExchange]
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'unify': {
        'name': 'Unify',
        'address_version_byte': 68,
        'bip44_coin_type': 0x8000007c,
        'private_key_prefix': 196,
        'script_hash_byte': None,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        "github_link": "https://github.com/SBDomains/unify-source",
        'header_hash_algo': None,
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [Cryptopia, NovaExchange], 'moon': [NovaExchange],
                'ltc': [Cryptopia, NovaExchange], 'usd': [],
                'doge': [Cryptopia, NovaExchange], 'eth': [NovaExchange],
            },
            'address_balance': [UnifyIquidus],
            'historical_transactions': [],
            'single_transaction': [UnifyIquidus],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [UnifyIquidus],
            'get_optimal_fee': []
        },
    },
    'dgb': {
        'name': 'Digibyte',
        'address_version_byte': 30,
        'bip44_coin_type': 0x80000014,
        'private_key_prefix': 128,
        'script_hash_byte': 5,
        'message_magic': b"\xfa\xc3\xb6\xda",
        'genesis_date': datetime(1, 1, 1),
        'github_link': None,
        'header_hash_algo': None,
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        "seed_nodes": [
            "seed.digibyte.co",
            "digiexplorer.info",
            "digihash.co"
        ],
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [BitZ], 'ltc': [], 'usd': [], 'doge': []
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'zcl': {
        'name': 'ZClassic',
        'address_version_byte': 7352,
        'bip44_coin_type': 0x80000093,
        'private_key_prefix': 128,
        'script_hash_byte': 0x1cbd,
        'genesis_date': datetime(2016, 10, 28, 7, 56),
        'message_magic': b"\x24\xe9\x27\x64",
        'github_link': "https://github.com/z-classic/zclassic",
        'header_hash_algo': 'double-sha256',
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'seed_nodes': [
            'dnsseed.zclassic.org',
            'dnsseed.indieonion.org',
            'dnsseed.rotorproject.org'
        ],
        'port': 8233,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [Bittrex, CCex, Cryptopia],
                'ltc': [], 'usd': [], 'doge': []
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'xlm': {
        'name': 'Stellar',
        'address_version_byte': None,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'script_hash_byte': None,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': None,
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [Bittrex, Poloniex, Kraken],
                'usd': [Poloniex], 'eth': [Bittrex]
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'b2x': {
        'name': 'Bitcoin 2x',
        'address_version_byte': None,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'script_hash_byte': None,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': None,
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [HitBTC, YoBit], 'usd': [HitBTC]
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'xem': {
        'name': 'Nem',
        'address_version_byte': None,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'script_hash_byte': None,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': None,
        'header_hash_algo': None,
        'transaction_hash_algo': None,
        'script_hash_algo': None,
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [Bittrex, Poloniex, Cryptopia, HitBTC, LiveCoin, YoBit],
                'usd': [YoBit, HitBTC, LiveCoin], 'eth': [Bittrex, HitBTC, LiveCoin, YoBit],
                'doge': [Cryptopia, YoBit], 'rur': [YoBit], 'ltc': [Cryptopia]
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'btg': {
        'name': 'Bitcoin Gold',
        'address_version_byte': 38,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'script_hash_byte': None,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': None,
        'header_hash_algo': None,
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [
                    Bittrex, BitFinex, BleuTrade, CexIO, Cryptopia, HitBTC,
                    KuCoin, NovaExchange, YoBit, OKEX, BitZ, EXX
                ],
                'ltc': [Cryptopia], 'krw': [CoinNest],
                'usd': [BitFinex, Bittrex, CexIO, HitBTC, YoBit], 'eur': [CexIO],
                'eth': [Bittrex, BleuTrade, HitBTC, KuCoin, NovaExchange, YoBit],
                'doge': [BleuTrade, Cryptopia, NovaExchange, YoBit], 'rur': [YoBit]
            },
            'address_balance': [Btgexp],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'mona': {
        'name': 'MonaCoin',
        'address_version_byte': 50,
        'bip44_coin_type': 0x80000016,
        'private_key_prefix': 176,
        'script_hash_byte': 55,
        'message_magic': None,
        'genesis_date': datetime(2013, 12, 31, 8, 44),
        'github_link': None,
        'header_hash_algo': None,
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [Bittrex, BleuTrade, BitBank], 'ltc': [], 'usd': [],
                'jpy': [BitBank, Zaif], 'qtum': [EXX], 'hsr': [EXX]
            },
            'address_balance': [MonaInsight],
            'historical_transactions': [MonaInsight],
            'single_transaction': [MonaInsight],
            'push_tx': [MonaInsight],
            'unspent_outputs': [MonaInsight],
            'get_block': [MonaInsight],
            'get_optimal_fee': []
        },
    },
    'btcp': {
        'name': 'Bitcoin Private',
        'address_version_byte': 19,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'script_hash_byte': None,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': None,
        'header_hash_algo': None,
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [HitBTC], 'ltc': [], 'usd': [], 'doge': []
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
    'bsv': {
        'name': 'BitcoinSV',
        'address_version_byte': 0,
        'bip44_coin_type': 0x800000ec,
        'private_key_prefix': 128,
        'script_hash_byte': None,
        'message_magic': b"\xe3\xe1\xf3\xe3",
        'genesis_date': datetime(2009, 1, 3, 18, 15, 5),
        'github_link': "https://github.com/bitcoin-sv/bitcoin-sv",
        'header_hash_algo': None,
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        'seed_nodes': [
            'seed.bitcoinsv.io',
            'seed.cascharia.com',
            'seed.satoshisvision.network',
            'stn-seed.bitcoinsv.io'
        ],
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': 50,
            'minutes_per_block': 10,
            'full_cap': 21000000,
            'blocks_per_era': 210000,
            'reward_ends_at_block': 6930000
        },
        'services': {
            'current_price': {
                'btc': [Bittrex], 'ltc': [], 'usd': [Bittrex], 'doge': []
            },
            'address_balance': [BCHSVExplorer],
            'historical_transactions': [BCHSVExplorer],
            'single_transaction': [BCHSVExplorer],
            'push_tx': [BCHSVExplorer],
            'unspent_outputs': [BCHSVExplorer],
            'get_block': [BCHSVExplorer],
            'get_optimal_fee': []
        },
    },
    # TEMPLATE
    '': {
        'name': '',
        'address_version_byte': None,
        'bip44_coin_type': None,
        'private_key_prefix': None,
        'script_hash_byte': None,
        'message_magic': None,
        'genesis_date': datetime(1, 1, 1),
        'github_link': None,
        'header_hash_algo': None,
        'transaction_hash_algo': 'double-sha256',
        'script_hash_algo': 'double-sha256',
        'port': None,
        'supply_data': {
            'method': 'standard',
            'start_coins_per_block': None,
            'minutes_per_block': None,
            'full_cap': None,
            'blocks_per_era': None,
            'reward_ends_at_block': None
        },
        'services': {
            'current_price': {
                'btc': [], 'ltc': [], 'usd': [], 'doge': []
            },
            'address_balance': [],
            'historical_transactions': [],
            'single_transaction': [],
            'push_tx': [],
            'unspent_outputs': [],
            'get_block': [],
            'get_optimal_fee': []
        },
    },
}
