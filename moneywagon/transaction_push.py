from .fetcher import Fetcher, SkipThisFetcher

class BlockrPushTransaction(Fetcher):
    def push_transaction(self, crypto, tx):
        crypto = crypto.lower()
        if crypto not in ['btc', 'ltc', 'mec', 'qrk', 'dgc', 'tbtc']:
            raise SkipThisFetcher("Blockr.io does not support this crypto: " + crypto)
        url = "http://%s.blockr.io/api/v1/tx/push" % crypto
        self.fetch_url(url)
        raise NotFinished()
