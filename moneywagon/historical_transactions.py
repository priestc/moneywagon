import arrow
from .fetcher import Fetcher, SkipThisFetcher

class BlockrHistoricalTransaction(Fetcher):
    def get_transactions(self, crypto, address):
        crypto = crypto.lower()
        if crypto not in ['btc', 'ltc', 'ppc', 'dgc', 'qrk', 'mec']:
            raise SkipThisFetcher('Blockr does not do %s' % crypto)

        url = 'http://%s.blockr.io/api/v1/address/txs/%s' % (crypto, address)
        response = self.fetch_url(url)

        transactions = []
        for tx in response.json()['data']['txs']:
            transactions.append(dict(
                date=arrow.get(tx['time_utc']).datetime,
                amount=tx['amount'],
                txid=tx['tx'],
                confirmations=tx['confirmations'],
            ))
        return transactions

class ChainSoHistoricalTransaction(Fetcher):
    def get_transactions(self, crypto, address):
        crypto = crypto.lower()
        if crypto != 'doge':
            raise SkipThisFetcher('Chain.so only for dogecoin')

        url = "https://chain.so/api/v2/get_tx_unspent/DOGE/" + address
        response = self.fetch_url(url)

        transactions = []
        for tx in response.json()['data']['txs']:
            transactions.append(dict(
                date=arrow.get(tx['time']).datetime,
                amount=tx['value'],
                txid=tx['txid'],
                confirmations=tx['confirmations'],
            ))
        return transactions
