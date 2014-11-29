from .fetcher import Fetcher

class BlockrAddressBalance(Fetcher):
    def get_balance(self, crypto, address):
        crypto = crypto.lower()
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
