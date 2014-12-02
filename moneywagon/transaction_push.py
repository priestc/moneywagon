from .Service import Service, SkipThisService

class BlockrPushTransaction(Service):
    def push_transaction(self, crypto, tx):
        crypto = crypto.lower()
        if crypto not in ['btc', 'ltc', 'mec', 'qrk', 'dgc', 'tbtc']:
            raise SkipThisService("Blockr.io does not support this crypto: " + crypto)
        url = "http://%s.blockr.io/api/v1/tx/push" % crypto
        self.get_url(url)
        raise NotFinished()
