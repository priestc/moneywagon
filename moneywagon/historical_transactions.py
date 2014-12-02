import arrow
from .service import Service, SkipThisService, AutoFallback

class BlockrHistoricalTransactions(Service):
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

class ChainSoHistoricalTransactions(Service):
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

class NXTPortalHistoricalTransaction(Service):
    supported_cryptos = ['nxt']

    def get_transactions(self, crypto, address):
        url = 'http://nxtportal.org/transactions/account/%s?num=50' % address
        response = self.get_url(url)
        transactions = []
        for tx in txs:
            transactions.append(dict(
                date=arrow.get(tx['time']).datetime,
                amount=tx['value'],
                txid=tx['txid'],
                confirmations=tx['confirmations'],
            ))

        return transactions

def insight_tx(tx, address):
    """
    The Insight API is weird and does not simply return the amount of coin sent
    per transaction. We have to iterate over the response data. This function
    can be reused by other services that have forked bitpay's insight code.
    """
    my_outs = [
        float(x['value']) for x in tx['vout'] if address in x['scriptPubKey']['addresses']
    ]
    return dict(
        amount=sum(my_outs),
        date=arrow.get(tx['time']).datetime,
        txid=tx['txid'],
        confirmations=tx['confirmations'],
    )

class BitpayInsightHistoricalTransaction(Service):
    supported_cryptos = ['btc']

    def get_transactions(self, crypto, address):
        url = "http://insight.bitpay.com/api/txs/?address=%s" % address
        response = self.get_url(url)

        transactions = []
        for tx in response.json()['txs']:
            transactions.append(insight_tx(tx, address))

        return transactions

class ReddcoinHistoricalTransaction(Service):
    supported_cryptos = ['rdd']

    def get_transactions(self, crypto, address):
        url = "http://live.reddcoin.com/api/txs/?address=%s" % address
        response = self.get_url(url)

        transactions = []
        for tx in response.json()['txs']:
            transactions = []
            for tx in response.json()['txs']:
                transactions.append(insight_tx(tx, address))

        return transactions

class HistoricalTransactions(AutoFallback):
    service_classes = [
        BlockrHistoricalTransactions,
        ChainSoHistoricalTransactions,
        NXTPortalHistoricalTransaction,
        ReddcoinHistoricalTransaction,
        BitpayInsightHistoricalTransaction,
    ]
    method_name = 'get_transactions'

    def get_transactions(self, crypto, address):
        crypto = crypto.lower()
        return self._try_each_service(crypto, address)

    def no_service_msg(self, crypto, address):
        return "Could not get transactions for: %s" % crypto
