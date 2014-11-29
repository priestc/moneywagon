import arrow
from .fetcher import Fetcher, SkipThisFetcher, AutoFallback

class BlockrHistoricalTransactions(Fetcher):
    supported_cryptos = ['btc', 'ltc', 'ppc', 'dgc', 'qrk', 'mec']

    def get_transactions(self, crypto, address):
        crypto = crypto.lower()
        url = 'http://%s.blockr.io/api/v1/address/txs/%s' % (crypto, address)
        response = self.get_url(url)

        transactions = []
        for tx in response.json()['data']['txs']:
            transactions.append(dict(
                date=arrow.get(tx['time_utc']).datetime,
                amount=tx['amount'],
                txid=tx['tx'],
                confirmations=tx['confirmations'],
            ))
        return transactions

class ChainSoHistoricalTransactions(Fetcher):
    supported_cryptos = ['doge']

    def get_transactions(self, crypto, address):
        crypto = crypto.lower()
        url = "https://chain.so/api/v2/get_tx_unspent/DOGE/" + address
        response = self.get_url(url)

        transactions = []
        for tx in response.json()['data']['txs']:
            transactions.append(dict(
                date=arrow.get(tx['time']).datetime,
                amount=tx['value'],
                txid=tx['txid'],
                confirmations=tx['confirmations'],
            ))
        return transactions

class HistoricalTransactions(AutoFallback):
    getter_classes = [
        BlockrHistoricalTransactions,
        ChainSoHistoricalTransactions
    ]
    method_name = 'get_transactions'

    def get_transactions(self, crypto, address):
        crypto = crypto.lower()
        return self._try_each_getter(crypto, address)

    def no_service_msg(self, crypto, address):
        return "Could not get transactions for: %s" % crypto
