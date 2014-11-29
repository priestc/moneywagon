from .fetcher import Fetcher

class BlockrPushTransaction(Fetcher):
    def push_transaction(self, crypto, tx):
        url = "http://%s.blockr.io/api/v1/tx/push" % crypto
