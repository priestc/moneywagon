from .fetcher import Fetcher

class BlockrAddressBalance(Fetcher):
    def get_balance(self, crypto, address):
        crypto = crypto.lower()
        if crypto not in ['btc', 'ltc', 'ppc', 'mec', 'qrk', 'dgc', 'tbtc']:
            raise SkipThisFetcher("Blockr.io does not support this crypto: " + crypto)
        url = "http://%s.blockr.io/api/v1/address/info/%s" % (crypto, address)
        response = self.fetch_url(url)
        return response.json()['data']['balance'], 'blockr.io'

class BlockChainInfoAddressBalance(Fetcher):
    def get_balance(self, crypto, address):
        crypto = crypto.lower()
        if crypto != 'btc':
            raise SkipThisGetter("Blockchain only does BTC")
        url = "http://blockchain.info/address/%s?format=json" % address
        response = self.fetch_url(url)
        return float(response.json()['final_balance']) * 1e-8, 'blockchain.info'

class DogeChainInfoAddressBalance(Fetcher):
    def get_balance(self, crypto, address):
        url = "https://dogechain.info/chain/Dogecoin/q/addressbalance/" + address
        response = self.fetch_url(url)
        return float(response.content), 'dogechain.info'
