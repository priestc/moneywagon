from .service import Service, AutoFallback

class BlockCypherAddressBalance(Service):
    supported_cryptos = ['btc', 'ltc', 'uro']

    def get_balance(self, crypto, address):
        crypto = crypto.lower()
        url = "http://api.blockcypher.com/v1/%s/main/addrs/%s" % (crypto, address)
        response = self.get_url(url)
        return response.json()['balance'] / 1.0e8

class BlockrAddressBalance(Service):
    supported_cryptos = ['btc', 'ltc', 'ppc', 'mec', 'qrk', 'dgc', 'tbtc']

    def get_balance(self, crypto, address):
        crypto = crypto.lower()
        url = "http://%s.blockr.io/api/v1/address/info/%s" % (crypto, address)
        response = self.get_url(url)
        return response.json()['data']['balance']

class BitEasyAddressBalance(Service):
    supported_cryptos = ['btc']

    def get_balance(self, crypto, address):
        url = "https://api.biteasy.com/blockchain/v1/addresses/" + address
        response = self.get_url(url)
        return response.json()['data']['balance'] / 1e8

class BlockChainInfoAddressBalance(Service):
    supported_cryptos = ['btc']

    def get_balance(self, crypto, address):
        crypto = crypto.lower()
        url = "http://blockchain.info/address/%s?format=json" % address
        response = self.get_url(url)
        return float(response.json()['final_balance']) * 1e-8

class DogeChainInfoAddressBalance(Service):
    supported_cryptos = ['doge']

    def get_balance(self, crypto, address):
        url = "https://dogechain.info/chain/Dogecoin/q/addressbalance/" + address
        response = self.get_url(url)
        return float(response.content)

class FeathercoinComAddressBalance(Service):
    supported_cryptos = ['ftc']

    def get_balance(self, crypto, address):
        url= "http://api.feathercoin.com/?output=balance&address=%s&json=1" % address
        response = self.get_url(url)
        return float(response.json()['balance'])

class VertcoinOrgAddressBalance(Service):
    supported_cryptos = ['vtc']

    def get_balance(self, crypto, address):
        url = "https://explorer.vertcoin.org/chain/Vertcoin/q/addressbalance/" + address
        response = self.get_url(url, verify=False)
        return float(response.content)

class NXTPortalAddressBalance(Service):
    supported_cryptos = ['nxt']

    def get_balance(self, crypto, address):
        url='http://nxtportal.org/nxt?requestType=getAccount&account=' + address
        response = self.get_url(url)
        return float(response.json()['balanceNQT']) * 1e-8

class CryptoIDAddresBalance(Service):
    supported_cryptos = [
        'drk', 'bc', 'bay', 'block', 'cann', 'uno', 'vrc', 'xc', 'uro', 'aur',
        'pot', 'cure', 'arch', 'swift', 'karm', 'dgc', 'lxc', 'sync', 'byc',
        'pc', 'fibre', 'i0c', 'nobl', 'gsx', 'flt', 'ccn', 'rlc', 'rby', 'apex',
        'vior', 'ltcd', 'zeit', 'carbon', 'super', 'dis', 'ac', 'vdo', 'ioc',
        'xmg', 'cinni', 'crypt', 'excl', 'mne', 'seed', 'qslv', 'maryj', 'key',
        'oc', 'ktk', 'voot', 'glc', 'drkc', 'mue', 'gb', 'piggy', 'jbs', 'grs',
        'icg', 'rpc', ''
    ]

    def get_balance(self, crypto, address):
        url ="http://chainz.cryptoid.info/%s/api.dws?q=getbalance&a=%s" % (crypto, address)
        return float(self.get_url(url).content)

class CryptapUSAddressBalance(Service):
    supported_cryptos = [
        'nmc', 'wds', 'ber', 'scn', 'sc0', 'wdc', 'nvc', 'cas', 'myr'
    ]
    def get_balance(self, crypto, address):
        url = "http://cryptap.us/%s/explorer/q/addressbalance/%s" % (crypto, address)
        return float(self.get_url(url).content)

class ReddcoinComAddressBalance(Service):
    supported_cryptos = ['rdd']

    def get_balance(self, crypto, address):
        url = "http://live.reddcoin.com/api/addr/%s/balance" % address
        return float(self.get_url(url).content) / 1e8

class AddressBalance(AutoFallback):
    service_classes = [
        BlockChainInfoAddressBalance,
        BitEasyAddressBalance,
        DogeChainInfoAddressBalance,
        VertcoinOrgAddressBalance,
        FeathercoinComAddressBalance,
        NXTPortalAddressBalance,
        BlockrAddressBalance,
        CryptoIDAddresBalance,
        BlockCypherAddressBalance,
        CryptapUSAddressBalance,
        ReddcoinComAddressBalance
    ]
    method_name = "get_balance"

    def get_balance(self, crypto, address):
        crypto = crypto.lower()
        return self._try_each_service(crypto, address)

    def no_service_msg(self, crypto, address):
        return "Could not get address balance for: %s" % crypto