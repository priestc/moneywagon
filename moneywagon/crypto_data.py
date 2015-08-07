from datetime import datetime
from .services import *

# taken from http://coinwik.org/List_of_all_DCs
# sorted by date released, copied over on Nov 27, 2014

crypto_data = {
    'btc': {
        'name': 'Bitcoin',
        'genesis_date': datetime(2009, 1, 12),
        'services': {
            'current_price': [
                Bitstamp, Winkdex, BTCE, BTER, Cryptonator
            ],
            'address_balance': [
                Toshi, BlockCypher, Blockr, BlockStrap, ChainSo, BitEasy,
                BlockChainInfo, BitcoinAbe
            ],
            'historical_transactions': [
                Blockr, Toshi, ChainSo
            ],
            'push_tx': [
                BlockChainInfo, Blockr, BlockStrap, ChainSo
            ]
        },
    },
    'ltc': {
        'name': 'Litecoin',
        'genesis_date': datetime(2011, 10, 7),
        'services': {
            'current_price': [
                BTCE, BTER, Cryptonator
            ],
            'address_balance': [
                BlockCypher, Blockr, BlockStrap, LitecoinAbe, ChainSo
            ],
            'historical_transactions': [
                Blockr, ChainSo
            ],
            'push_tx': [
                Blockr, BlockStrap, ChainSo
            ]
        },
    },
    'ppc': {
        'name': 'Peercoin',
        'genesis_date': datetime(2012, 8, 19),
        'services': {
            'current_price': [
                BTCE, BTER, Cryptonator
            ],
            'address_balance': [
                Blockr
            ],
            'historical_transactions': [
                Blockr
            ],
            'push_tx': [
                Blockr
            ]
        },
    },
    'doge': {
        'name': 'Dogecoin',
        'genesis_date': datetime(2013, 12, 6),
        'services': {
            'current_price': [
                BTCE, BTER, Cryptonator
            ],
            'address_balance': [
                DogeChainInfo, BlockStrap
            ],
            'historical_transactions': [
                ChainSo
            ],
            'push_tx': [
                BlockStrap
            ]
        },
    },
    'nxt': {
        'name': 'Nxt',
        'genesis_date': datetime(2013, 10, 29),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                NXTPortal
            ],
            'historical_transactions': [
                NXTPortal
            ],
            'push_tx': [

            ]
        },
    },
    'myr': {
        'name': 'MyriadCoin',
        'genesis_date': datetime(2014, 2, 23),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                MYRCryptap, CryptapUS, BirdOnWheels
            ],
            'historical_transactions': [
                MYRCryptap, BirdOnWheels
            ],
            'push_tx': [
                MYRCryptap
            ]
        },
    },
    'vtc': {
        'name': 'Vertcoin',
        'genesis_date': datetime(2014, 1, 8),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                ThisIsVTC
            ],
            'historical_transactions': [
                ThisIsVTC
            ],
            'push_tx': [
                ThisIsVTC
            ]
        },
    },
    'ftc': {
        'name': 'Feathercoin',
        'genesis_date': datetime(2013, 4, 16),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                FTCe
            ],
            'historical_transactions': [
                FTCe
            ],
            'push_tx': [
                FTCe
            ]
        },
    },
    'drk': {
        'name': 'Dash',
        'genesis_date': datetime(2014, 1, 19),
        'services': {
            'current_price': [
                Cryptonator
            ],
            'address_balance': [
                CryptoID
            ],
            'historical_transactions': [

            ],
            'push_tx': [

            ]
        },
    },


    # these ones below need to be modified to match the above format

    'nmc': ['Namecoin', datetime(2011, 4, 18)],
    'tk':  ['TimeKoin', datetime(2011, 5, 27)],
    'dvc': ['DevCoin', datetime(2011, 8, 5)],
    'ixc': ['IxCoin', datetime(2011, 8, 10)],
    'bcn': ['Bytecoin', datetime(2012, 7, 4)],
    'bte': ['Bytecoin', datetime(2012, 7, 4)],
    'bqc': ['BBQCoin', datetime(2012, 7, 15)],
    'str': ['StarCoin', datetime(2012, 7, 19)],

    'nvc': ['NovaCoin', datetime(2012, 10, 1)],
    'trc': ['TerraCoin', datetime(2012, 10, 26)],
    'frc': ['Freicoin', datetime(2012, 12, 21)],

    'btb': ['BitBar', datetime(2013, 4, 1)],
    'mnc': ['MinCoin', datetime(2013, 4, 3)],
    'net': ['NetCoin', datetime(2013, 4, 7)],
    'nan': ['NanoToken', datetime(2013, 4, 8)],

    'xrp': ['Ripple', datetime(2011, 3, 1)],
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
    'uno': ['Unobtanium', datetime(2013, 10, 17)],
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
    'tips':['FedoraCoin', datetime(2013, 12, 21)],
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
    'xcp': ['Counterparty', datetime(2014, 1, 2)],
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
    'rdd': ['Reddcoin', datetime(2014, 1, 20)],
    'cash':['CashCoin', datetime(2014, 1, 20)],
    'mry': ['MurrayCoin', datetime(2014, 1, 20)],
    'pot': ['Potcoin', datetime(2014, 1, 21)],
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
    'aur': ['Auroracoin', datetime(2014, 2, 2)],
    'pop': ['PopularCoin', datetime(2014, 2, 2)],
    'lbt': ['Litebar', datetime(2014, 2, 2)],
    'corg':['CorgiCoin', datetime(2014, 2, 2)],
    'karm':['Karmacoin', datetime(2014, 2, 4)],
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
    'flap':['Flappycoin', datetime(2014, 2, 14)],
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
    'dime':['Dimecoin', datetime(2014, 12, 23)],
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
