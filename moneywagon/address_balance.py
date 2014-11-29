from .fetcher import Fetcher, AutoFallback

class BlockrAddressBalance(Fetcher):
    supported_cryptos = ['btc', 'ltc', 'ppc', 'mec', 'qrk', 'dgc', 'tbtc']

    def get_balance(self, crypto, address):
        crypto = crypto.lower()
        url = "http://%s.blockr.io/api/v1/address/info/%s" % (crypto, address)
        response = self.get_url(url)
        return response.json()['data']['balance'], 'blockr.io'

class BlockChainInfoAddressBalance(Fetcher):
    supported_cryptos = ['btc']

    def get_balance(self, crypto, address):
        crypto = crypto.lower()
        url = "http://blockchain.info/address/%s?format=json" % address
        response = self.get_url(url)
        return float(response.json()['final_balance']) * 1e-8, 'blockchain.info'

class DogeChainInfoAddressBalance(Fetcher):
    supported_cryptos = ['doge']

    def get_balance(self, crypto, address):
        url = "https://dogechain.info/chain/Dogecoin/q/addressbalance/" + address
        response = self.get_url(url)
        return float(response.content), 'dogechain.info'

class FeathercoinComAddressBalance(Fetcher):
    supported_cryptos = ['ftc']

    def get_balance(self, crypto, address):
        url= "http://api.feathercoin.com/?output=balance&address=%s&json=1" % address
        response = self.get_url(url)
        return float(response.json()['balance']), 'feathercoin.com'

class VertcoinOrgAddressBalance(Fetcher):
    def get_balance(self):
        url = "https://explorer.vertcoin.org/chain/Vertcoin/q/addressbalance/" + address
        response = self.get_url(url, verify=False)
        return float(response.content)

class AddressBalance(AutoFallback):
    getter_classes = [
        BlockChainInfoAddressBalance, DogeChainInfoAddressBalance, VertcoinOrgAddressBalance,
        FeathercoinComAddressBalance, BlockrAddressBalance
    ]
    method_name = "get_balance"

    def get_balance(self, crypto, address):
        crypto = crypto.lower()
        return self._try_each_getter(crypto, address)

    def no_return_value(self, crypto, address):
        return 0
