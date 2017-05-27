from moneywagon.services import Service, BitcoinAbe, BitpayInsight

class BlockStrap(Service):
    """
    Documentation here: http://docs.blockstrap.com/en/api/
    """
    #decomissioned
    service_id = 10
    domain = 'http://api.blockstrap.com'
    supported_cryptos = ['btc', 'ltc', 'drk', 'doge']
    api_homepage = "http://blockstrap.com/blog/deprecated/"

    def get_balance(self, crypto, address, confirmations=None):
        url = "%s/v0/%s/address/id/%s" % (self.domain, crypto, address)
        response = self.get_url(url).json()
        return response['data']['address']['balance'] / 1e8

    def push_tx(self, crypto, tx_hex):
        url = "%s/v0/%s/transaction/relay/%s" % (self.domain, crypto, tx_hex)
        return self.get_url(url).json()['data']['id']

    def get_transactions(self, crypto, address):
        url = "%s/v0/%s/address/transactions/%s" % (self.domain, crypto, address)
        txs = []
        for tx in self.get_url(url).json()['data']['address']['transactions']:
            s_amount = tx['tx_address_input_value'] or tx['tx_address_output_value'] * -1
            txs.append(dict(
                date=arrow.get(tx['block_time']).datetime,
                amount=s_amount / 1e8,
                confirmations=tx['confirmations'],
                txid=tx['id'],
            ))
        return txs

    def get_unspent_outputs(self, crypto, address):
        url = "%s/v0/%s/address/unspents/%s" % (self.domain, crypto, address)
        utxos = []
        for utxo in self.get_url(url).json()['data']['address']['transactions']:
            utxos.append(dict(
                amount=utxo['tx_address_value'],
                address=address,
                output="%s:%s" % (utxo['id'].lower(), utxo['tx_address_tx_pos']),
                confirmations=utxo['confirmations']
            ))
        return utxos

    def get_block(self, crypto, block_hash='', block_number='', latest=False):
        if block_hash:
            url = "%s/v0/%s/block/id/%s" % (self.domain, crypto, block_hash)
            b = "block"
        elif block_number:
            url = "%s/v0/%s/block/height/%s" % (self.domain, crypto, block_number)
            b = "blocks"
        elif latest:
            url = "%s/v0/%s/block/latest" % (self.domain, crypto)
            b = 'block'

        r = self.get_url(url).json()['data'][b]

        if block_number:
            r = r[0]

        return dict(
            block_number=r['height'],
            confirmations=r["confirmations"],
            time=arrow.get(r['time_display']).datetime,
            sent_value=r["output_value"] / 1e8,
            total_fees=r["fees"] / 1e8,
            size=r['size'],
            hash=r['id'].lower(),
            merkle_root=r['merkel_root'].lower(),
            previous_hash=r['prev_block_id'].lower(),
            next_hash=r['next_block_id'].lower(),
            txids=sorted(x['id'] for x in r['transactions']),
            tx_count=len(r['transactions'])
        )

class LitecoinAbe(BitcoinAbe):
    service_id = 16
    supported_cryptos = ['ltc']
    base_url = "http://bitcoin-abe.info/chain/Litecoin"


class NamecoinAbe(BitcoinAbe):
    service_id = 17
    supported_cryptos = ['nmc']
    base_url = "http://bitcoin-abe.info/chain/Namecoin"

class CoinSwap(Service):
    service_id = 26
    def get_current_price(self, crypto, fiat):
        chunk = ("%s/%s" % (crypto, fiat)).upper()
        url = "https://api.coin-swap.net/market/stats/%s" % chunk
        response = self.get_url(url).json()
        return float(response['lastprice']), 'coin-swap'


class ExCoIn(Service):
    service_id = 27
    # decommissioned
    def get_current_price(self, crypto, fiat):
        url = "https://api.exco.in/v1/exchange/%s/%s" % (fiat, crypto)
        response = self.get_url(url).json()
        return float(response['last_price']), 'exco.in'

class TheBitInfo(BitpayInsight):
    service_id = 29
    supported_cryptos = ['btc']
    domain = "insight.thebit.info"
    name = "TheBit.info"

class FTCc(BitpayInsight):
    service_id = 34
    supported_cryptos = ['ftc']
    domain = "block.ftc-c.com"
    name = "Feathercoin China"

class FeathercoinCom(Service):
    service_id = 21
    supported_cryptos = ['ftc']
    api_homepage = "http://api.feathercoin.com/"
    name = "Feathercoin.com"

    def get_balance(self, crypto, address, confirmations=1):
        url= "http://api.feathercoin.com/?output=balance&address=%s&json=1" % address
        response = self.get_url(url)
        return float(response.json()['balance'])

class Toshi(Service):
    api_homepage = "https://toshi.io/docs/"
    service_id = 6
    url = "https://bitcoin.toshi.io/api/v0"
    name = "Toshi"

    supported_cryptos = ['btc']

    def check_error(self, response):
        if 'error' in response.json():
            raise ServiceError("Toshi returned error: %s" % response.json()['error'])

        if response.status_code == 404:
            return # don't skip on 404

        super(Toshi, self).check_error(response)

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/addresses/%s" % (self.url, address)
        response = self.get_url(url).json()
        return response['balance'] / 1e8

    def get_transactions(self, crypto, address, confirmations=1):
        url = "%s/addresses/%s/transactions" % (self.url, address)
        response = self.get_url(url)
        if response.status_code == 404:
            return []

        j = response.json()
        transactions = []
        for tx in j.get('unconfirmed_transactions', []) + j['transactions']:
            transactions.append(dict(
                amount=sum([x['amount'] / 1e8 for x in tx['outputs'] if address in x['addresses']]),
                txid=tx['hash'],
                date=arrow.get(tx['block_time']).datetime if tx.get('block_time', False) else None,
                confirmations=tx['confirmations']
            ))

        return transactions

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = "%s/addresses/%s/unspent_outputs" % (self.url, address)
        response = self.get_url(url).json()
        utxos = []
        for utxo in response:
            cons = utxo['confirmations']
            if cons < confirmations:
                continue
            utxos.append(dict(
                amount=utxo['amount'],
                address=address,
                output="%s:%s" % (utxo['transaction_hash'], utxo['output_index']),
                confirmations=cons,
                vout=utxo['output_index'],
                txid=utxo['transaction_hash'],
                scriptPubKey=utxo['script_hex'],
                scriptPubKey_asm=utxo['script']
            ))
        return utxos


    def push_tx(self, crypto, tx_hex):
        url = "%s/transactions/%s" % (self.url, tx_hex)
        return self.get_url(url).json()['hash']

    def get_block(self, crypto, block_hash='', block_number='', latest=False):
        if latest:
            url = "%s/blocks/latest" % self.url
        else:
            url = "%s/blocks/%s%s" % (
                self.url, block_hash if block_hash != '' else '',
                block_number if block_number != '' else ''
            )

        r = self.get_url(url).json()
        return dict(
            block_number=r['height'],
            confirmations=r['confirmations'],
            time=arrow.get(r['time']).datetime,
            sent_value=r['total_out'] / 1e8,
            total_fees=r['fees'] / 1e8,
            mining_difficulty=r['difficulty'],
            size=r['size'],
            hash=r['hash'],
            merkle_root=r['merkle_root'],
            previous_hash=r['previous_block_hash'],
            next_hash=r['next_blocks'][0]['hash'] if len(r['next_blocks']) else None,
            txids=sorted(r['transaction_hashes']),
            tx_count=len(r['transaction_hashes'])
        )

class NeoCrypto(BitpayInsight):
    service_id = 51
    protocol = "https"
    domain = "insight.neocrypto.io"
    api_tag = 'insight-api'
    name = "Neocrypt"

class VertcoinInfo(Iquidus):
    service_id = 56
    name = "Vertcoin.info"
    base_url = "http://explorer.vertcoin.info"
    supported_cryptos = ['vtc']
