from .core import Service, NoService, NoData, SkipThisService, currency_to_protocol
import arrow

class Bitstamp(Service):
    supported_cryptos = ['btc']

    def get_current_price(self, crypto, fiat):
        if fiat.lower() != 'usd':
            raise SkipThisService('Bitstamp only does USD->BTC')

        url = "https://www.bitstamp.net/api/ticker/"
        response = self.get_url(url).json()
        return (float(response['last']), 'bitstamp')


class BlockCypher(Service):
    supported_cryptos = ['btc', 'ltc', 'uro']

    def get_balance(self, crypto, address, confirmations=1):
        url = "http://api.blockcypher.com/v1/%s/main/addrs/%s" % (crypto, address)
        response = self.get_url(url)
        return response.json()['balance'] / 1.0e8


class BlockSeer(Service):
    """
    This service has no publically documented API, this code was written
    from looking through chrome dev toolbar.
    """
    supported_cryptos = ['btc']

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://www.blockseer.com/api/addresses/%s" % address
        return self.get_url(url).json()['data']['balance'] / 1e8

    def get_transactions(self, crypo, address):
        url = "https://www.blockseer.com/api/addresses/%s/transactions?filter=all" % address
        transactions = []
        for tx in self.get_url(url).json()['data']['address']['transactions']:
            transactions.append(dict(
                date=arrow.get(tx['time']).datetime,
                amount=tx['delta'] / 1e8,
                txid=tx['hash'],
            ))
        return transactions


class SmartBitAU(Service):
    base_url = "https://api.smartbit.com.au/v1/blockchain"
    supported_cryptos = ['btc']

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/address/%s" % (self.base_url, address)
        r = self.get_url(url).json()

        confirmed = float(r['address']['confirmed']['balance'])
        if confirmations > 1:
            return confirmed
        else:
            return confirmed + float(r['address']['unconfirmed']['balance'])

    def get_balance_multi(self, crypto, addresses, confirmations=1):
        url = "%s/address/%s" % (self.base_url, ",".join(addresses))
        response = self.get_url(url).json()

        ret = {}
        for data in response['addresses']:
            bal = float(data['confirmed']['balance'])
            if confirmations == 0:
                bal += float(data['unconfirmed']['balance'])
            ret[data['address']] = bal

        return ret

    def get_transactions(self, crypto, address, confirmations=1):
        url = "%s/address/%s" % (self.base_url, address)
        transactions = []
        for tx in self.get_url(url).json()['address']['transactions']:
            out_amount = sum(float(x['value']) for x in tx['outputs'] if address in x['addresses'])
            in_amount = sum(float(x['value']) for x in tx['inputs'] if address in x['addresses'])
            transactions.append(dict(
                amount=out_amount - in_amount,
                date=arrow.get(tx['time']).datetime,
                fee=float(tx['fee']),
                txid=tx['txid'],
                confirmations=tx['confirmations'],
            ))
        return transactions

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = "%s/address/%s/unspent" % (self.base_url, address)
        utxos = []
        for utxo in self.get_url(url).json()['unspent']:
            utxos.append(dict(
                amount=utxo['value_int'],
                output="%s:%s" % (utxo['txid'], utxo['n']),
                address=address,
            ))
        return utxos

    def push_tx(self, crypto, tx_hex):
        """
        This method is untested.
        """
        url = "%s/pushtx" % self.base_url
        return self.post_url(url, {'hex': tx_hex}).content

    def get_mempool(self):
        url = "%s/transactions/unconfirmed?limit=1000" % self.base_url
        txs = []
        for tx in self.get_url(url).json()['transactions']:
            txs.append(dict(
                first_seen=arrow.get(tx['first_seen']).datetime,
                size=tx['size'],
                txid=tx['txid'],
                fee=float(tx['fee']),
            ))
        return txs


class Blockr(Service):
    supported_cryptos = ['btc', 'ltc', 'ppc', 'mec', 'qrk', 'dgc', 'tbtc']

    def get_balance(self, crypto, address, confirmations=1):
        url = "http://%s.blockr.io/api/v1/address/info/%s" % (crypto, address)
        response = self.get_url(url)
        return response.json()['data']['balance']

    def get_transactions(self, crypto, address, confirmations=1):
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

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = "http://%s.blockr.io/api/v1/address/unspent/%s" % (crypto, address)
        utxos = []
        for utxo in self.get_url(url).json()['data']['unspent']:
            cons = utxo['confirmations']
            if cons < confirmations:
                continue
            utxos.append(dict(
                amount=currency_to_protocol(utxo['amount']),
                address=address,
                output="%s:%s" % (utxo['tx'], utxo['n']),
                confirmations=cons
            ))
        return utxos
    get_unspent_outputs.obeys_confirmations = True


    def push_tx(self, crypto, tx_hex):
        url = "http://%s.blockr.io/api/v1/tx/push" % crypto
        resp = self.post_url(url, {'tx': tx_hex}).json()
        if resp['status'] == 'fail':
            raise ValueError(
                "Blockr returned error: %s %s %s" % (
                    resp['code'], resp['data'], resp['message']
                )
            )
        return resp['data']

    def get_block(self, crypto, block_hash='', block_number='', latest=False):
        url ="http://%s.blockr.io/api/v1/block/info/%s%s%s" % (
            crypto, block_hash, block_number, 'latest' if latest else ''
        )
        r = self.get_url(url).json()['data']
        return dict(
            block_number=r['nb'],
            confirmations=r['confirmations'],
            time=arrow.get(r['time_utc']).datetime,
            sent_value=r['vout_sum'],
            total_fees=float(r['fee']),
            mining_difficulty=r['difficulty'],
            size=r['size'],
            hash=r['hash'],
            merkle_root=r['merkleroot'],
            previous_hash=r['prev_block_hash'],
            next_hash=r['next_block_hash'],
            tx_count=r['nb_txs'],
        )


class Toshi(Service):
    url = "https://bitcoin.toshi.io/api/v0"

    supported_cryptos = ['btc']

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/addresses/%s" % (self.url, address)
        response = self.get_url(url).json()
        return response['balance'] / 1e8

    def get_transactions(self, crypto, address, confirmations=1):
        """
        This call also returns unconfirmed transactions.
        """
        url = "%s/addresses/%s/transactions" % (self.url, address)
        response = self.get_url(url).json()

        if confirmations == 0:
            to_iterate = response['transactions'] + response['unconfirmed_transactions']
        else:
            to_iterate = response['transactions']

        transactions = []
        for tx in to_iterate:
            transactions.append(dict(
                amount=sum([x['amount'] / 1e8 for x in tx['outputs'] if address in x['addresses']]),
                txid=tx['hash'],
                date=arrow.get(tx['block_time']).datetime,
                confirmations=tx['confirmations']
            ))
        return transactions

    def push_tx(self, crypto, tx_hex):
        url = "%s/transactions/%s" % (self.url, tx_hex)
        return self.get_url(url).json()['hash']

    def get_block(self, crypto, block_hash='', block_number='', latest=False):
        if latest:
            url = "%s/blocks/latest" % self.url
        else:
            url = "%s/blocks/%s%s" % (self.url, block_hash, block_number)

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


class BTCE(Service):
    def get_current_price(self, crypto, fiat):
        pair = "%s_%s" % (crypto.lower(), fiat.lower())
        url = "https://btc-e.com/api/3/ticker/" + pair
        response = self.get_url(url).json()
        return (response[pair]['last'], 'btc-e')


class Cryptonator(Service):
    def get_current_price(self, crypto, fiat):
        pair = "%s-%s" % (crypto, fiat)
        url = "https://www.cryptonator.com/api/ticker/%s" % pair
        response = self.get_url(url).json()
        return float(response['ticker']['price']), 'cryptonator'


class Winkdex(Service):
    supported_cryptos = ['btc']

    def get_current_price(self, crypto, fiat):
        if fiat != 'usd':
            raise SkipThisService("winkdex is btc->usd only")
        url = "https://winkdex.com/api/v0/price"
        return self.get_url(url).json()['price'] / 100.0, 'winkdex'


class BlockStrap(Service):
    """
    Documentation here: http://docs.blockstrap.com/en/api/
    """
    domain = 'http://api.blockstrap.com'
    supported_cryptos = ['btc', 'ltc', 'drk', 'doge']

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


class ChainSo(Service):
    base_url = "https://chain.so/api/v2"
    supported_cryptos = ['doge', 'btc', 'ltc']

    def get_current_price(self, crypto, fiat):
        url = "%s/get_price/%s/%s" % (self.base_url, crypto, fiat)
        resp = self.get_url(url).json()
        items = resp['data']['prices']
        if len(items) == 0:
            raise SkipThisService("Chain.so can't get price for %s/%s" % (crypto, fiat))
        return float(items[0]['price']), "%s via Chain.so" % items[0]['exchange']

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/get_address_balance/%s/%s/%s" % (
            self.base_url, crypto, address, confirmations
        )
        response = self.get_url(url)
        return float(response.json()['data']['confirmed_balance'])

    def get_transactions(self, crypto, address, confirmations=1):
        url = "%s/get_tx_received/%s/%s" % (self.base_url, crypto, address)
        response = self.get_url(url)

        transactions = []
        for tx in response.json()['data']['txs']:
            tx_cons = int(tx['confirmations'])
            if tx_cons < confirmations:
                continue
            transactions.append(dict(
                date=arrow.get(tx['time']).datetime,
                amount=float(tx['value']),
                txid=tx['txid'],
                confirmations=tx_cons,
            ))

        return transactions

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = "%s/get_tx_unspent/%s/%s" %(self.base_url, crypto, address)
        utxos = []
        for utxo in self.get_url(url).json()['data']['txs']:
            utxos.append(dict(
                amount=currency_to_protocol(utxo['value']),
                address=address,
                output="%s:%s" % (utxo['txid'], utxo['output_no']),
                confirmations=utxo['confirmations']
            ))
        return utxos


    def push_tx(self, crypto, tx_hex):
        url = "%s/send_tx/%s" % (self.base_url, crypto)
        resp = self.post_url(url, {'tx_hex': tx_hex})
        return resp.json()['data']['txid']

    def get_block(self, crypto, block_number='', block_hash='', latest=False):
        if latest:
            raise SkipThisService("This service can't get block by latest")
        else:
            url = "%s/block/%s/%s%s" % (
                self.base_url, crypto, block_number, block_hash
            )
        r = self.get_url(url).json()['data']
        return dict(
            block_number=r['block_no'],
            confirmations=r['confirmations'],
            time=arrow.get(r['time']).datetime,
            sent_value=float(r['sent_value']),
            total_fees=float(r['fee']),
            mining_difficulty=float(r['mining_difficulty']),
            size=r['size'],
            hash=r['blockhash'],
            merkle_root=r['merkleroot'],
            previous_hash=r['previous_blockhash'],
            next_hash=r['next_blockhash'],
            txids=sorted([t['txid'] for t in r['txs']])
        )


class CoinPrism(Service):
    base_url = "https://api.coinprism.com/v1"
    supported_cryptos = ['btc']

    def get_balance(self, crypto, address, confirmations=None):
        url = "%s/addresses/%s" % (self.base_url, address)
        resp = self.get_url(url).json()
        return resp['balance'] / 1e8

    def get_transactions(self, crypto, address):
        url = "%s/addresses/%s/transactions" % (self.base_url, address)
        transactions = []
        for tx in self.get_url(url).json():
            transactions.append(dict(
                amount=sum([x['value'] / 1e8 for x in tx['outputs'] if address in x['addresses']]),
                txid=tx['hash'],
                date=arrow.get(tx['block_time']).datetime,
                confirmations=tx['confirmations']
            ))

        return transactions

    def get_unspent_outputs(self, crypto, address):
        url = "%s/addresses/%s/unspents" % (self.base_url, address)
        transactions = []
        for tx in self.get_url(url).json():
            if address in tx['addresses']:
                transactions.append(dict(
                    amount=tx['value'],
                    address=address,
                    output="%s:%s" % (tx['transaction_hash'], tx['output_index']),
                    confirmations=tx['confirmations']
                ))

        return transactions

    def push_tx(self, crypto, tx_hex):
        """
        Note: This one has not been tested yet.
        http://docs.coinprism.apiary.io/#reference/transaction-signing-and-broadcasting/push-a-signed-raw-transaction-to-the-network/post
        """
        url = "%s/sendrawtransaction"
        return self.post_url(url, tx_hex).content


class BitEasy(Service):
    """
    Most functions from this servie require an API key. therefore only
    address balance is supported at this time.
    """
    supported_cryptos = ['btc']

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://api.biteasy.com/blockchain/v1/addresses/" + address
        response = self.get_url(url)
        return response.json()['data']['balance'] / 1e8


class BlockChainInfo(Service):
    supported_cryptos = ['btc']

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://blockchain.info/address/%s?format=json" % address
        response = self.get_url(url)
        return float(response.json()['final_balance']) * 1e-8

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = "https://blockchain.info/unspent?address=%s" % address
        utxos = []
        for utxo in self.get_url(url).json()['unspent_outputs']:
            if utxo['confirmations'] < confirmations:
                continue # don't return if too few confirmations

            utxos.append(dict(
                output="%s:%s" % (utxo['tx_hash_big_endian'], utxo['tx_output_n']),
                amount=utxo['value'],
                address=address,
            ))
        return utxos


##################################

class BitcoinAbe(Service):
    supported_cryptos = ['btc']
    base_url = "http://bitcoin-abe.info/chain/Bitcoin"

    def get_balance(self, crypto, address, confirmations=1):
        url = self.base_url + "/q/addressbalance/" + address
        response = self.get_url(url)
        return float(response.content)


class LitecoinAbe(BitcoinAbe):
    supported_cryptos = ['ltc']
    base_url = "http://bitcoin-abe.info/chain/Litecoin"


class NamecoinAbe(BitcoinAbe):
    supported_cryptos = ['nmc']
    base_url = "http://bitcoin-abe.info/chain/Namecoin"


class DogeChainInfo(BitcoinAbe):
    supported_cryptos = ['doge']
    base_url = "https://dogechain.info/chain/Dogecoin"


class AuroraCoinEU(BitcoinAbe):
    supported_cryptos = ['aur']
    base_url = 'http://blockexplorer.auroracoin.eu/chain/AuroraCoin'


class Atorox(BitcoinAbe):
    supported_cryptos = ['aur']
    base_url = "http://auroraexplorer.atorox.net/chain/AuroraCoin"

##################################

class FeathercoinCom(Service):
    supported_cryptos = ['ftc']

    def get_balance(self, crypto, address, confirmations=1):
        url= "http://api.feathercoin.com/?output=balance&address=%s&json=1" % address
        response = self.get_url(url)
        return float(response.json()['balance'])


class NXTPortal(Service):
    supported_cryptos = ['nxt']

    def get_balance(self, crypto, address, confirmations=1):
        url='http://nxtportal.org/nxt?requestType=getAccount&account=' + address
        response = self.get_url(url)
        return float(response.json()['balanceNQT']) * 1e-8

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


class CryptoID(Service):
    supported_cryptos = [
        'dash', 'bc', 'bay', 'block', 'cann', 'uno', 'vrc', 'xc', 'uro', 'aur',
        'pot', 'cure', 'arch', 'swift', 'karm', 'dgc', 'lxc', 'sync', 'byc',
        'pc', 'fibre', 'i0c', 'nobl', 'gsx', 'flt', 'ccn', 'rlc', 'rby', 'apex',
        'vior', 'ltcd', 'zeit', 'carbon', 'super', 'dis', 'ac', 'vdo', 'ioc',
        'xmg', 'cinni', 'crypt', 'excl', 'mne', 'seed', 'qslv', 'maryj', 'key',
        'oc', 'ktk', 'voot', 'glc', 'drkc', 'mue', 'gb', 'piggy', 'jbs', 'grs',
        'icg', 'rpc', ''
    ]

    def get_balance(self, crypto, address, confirmations=1):
        url ="http://chainz.cryptoid.info/%s/api.dws?q=getbalance&a=%s" % (crypto, address)
        return float(self.get_url(url).content)


class CryptapUS(Service):
    supported_cryptos = [
        'nmc', 'wds', 'ber', 'scn', 'sc0', 'wdc', 'nvc', 'cas', 'myr'
    ]
    def get_balance(self, crypto, address, confirmations=1):
        url = "http://cryptap.us/%s/explorer/q/addressbalance/%s" % (crypto, address)
        return float(self.get_url(url).content)


class BTER(Service):
    def get_current_price(self, crypto, fiat):
        url_template = "http://data.bter.com/api/1/ticker/%s_%s"
        url = url_template % (crypto, fiat)

        response = self.get_url(url).json()

        if response['result'] == 'false': # bter api returns this as string
            # bter doesn't support this pair, we need to make 2 calls and
            # do the math ourselves. The extra http request isn't a problem because
            # of caching. BTER only has USD, BTC and CNY
            # markets, so any other fiat will likely fail.

            url = url_template % (crypto, 'btc')
            response = self.get_url(url)
            altcoin_btc = float(response['last'])

            url = url_template % ('btc', fiat)
            response = self.get_url(url)
            btc_fiat = float(response['last'])

            return (btc_fiat * altcoin_btc), 'bter (calculated)'

        return float(response['last'] or 0), 'bter'


class CoinSwap(Service):
    def get_current_price(self, crypto, fiat):
        chunk = ("%s/%s" % (crypto, fiat)).upper()
        url = "https://api.coin-swap.net/market/stats/%s" % chunk
        response = self.get_url(url).json()
        return float(response['lastprice']), 'coin-swap'


class ExCoIn(Service):
    # decommissioned
    def get_current_price(self, crypto, fiat):
        url = "https://api.exco.in/v1/exchange/%s/%s" % (fiat, crypto)
        response = self.get_url(url).json()
        return float(response['last_price']), 'exco.in'

################################################

class BitpayInsight(Service):
    supported_cryptos = ['btc']
    domain = "http://insight.bitpay.com"

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/api/addr/%s/balance" % (self.domain, address)
        return float(self.get_url(url).content) / 1e8

    def get_transactions(self, crypto, address):
        url = "%s/api/txs/?address=%s" % (self.domain, address)
        response = self.get_url(url)

        transactions = []
        for tx in response.json()['txs']:
            my_outs = [
                float(x['value']) for x in tx['vout'] if address in x['scriptPubKey']['addresses']
            ]
            transactions.append(dict(
                amount=sum(my_outs),
                date=arrow.get(tx['time']).datetime,
                txid=tx['txid'],
                confirmations=tx['confirmations'],
            ))

        return transactions

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = "%s/api/addr/%s/utxo?noCache=1" % (self.domain, address)
        utxos = []
        for utxo in self.get_url(url).json():
            utxos.append(dict(
                output="%s:%s" % (utxo['txid'], utxo['vout']),
                amount=currency_to_protocol(utxo['amount']),
                confirmations=utxo['confirmations'],
                address=address
            ))
        return utxos

    def get_block(self, crypto, block_number='', block_hash='', latest=False):
        if block_number:
            url = "%s/api/block-index/%s" % (self.domain, block_number)
        elif block_hash:
            url = "%s/api/block/%s" % (self.domain, block_hash)
        elif latest:
            raise ValueError("Can't get current block.")

        r = self.get_url(url).json()
        return dict(
            block_number=r['block_no'],
            confirmations=r['confirmations'],
            time=arrow.get(r['time']).datetime,
            sent_value=float(r['sent_value']),
            total_fees=float(r['fee']),
            mining_difficulty=float(r['mining_difficulty']),
            size=r['size'],
            hash=r['blockhash'],
            merkle_root=r['merkleroot'],
            previous_hash=r['previous_blockhash'],
            next_hash=r['next_blockhash'],
            txids=[t['txid'] for t in r['txs']],
            tx_count=len(r['txs'])
        )


class TheBitInfo(BitpayInsight):
    supported_cryptos = ['btc']
    domain = "http://insight.thebit.info/"


class MYRCryptap(BitpayInsight):
    supported_cryptos = ['myr']
    domain = "http://insight-myr.cryptap.us/"


class BirdOnWheels(BitpayInsight):
    supported_cryptos = ['myr']
    domain = "http://birdonwheels5.no-ip.org:3000"


class ThisIsVTC(BitpayInsight):
    supported_cryptos = ['vtc']
    domain = "http://explorer.thisisvtc.com"


class ReddcoinCom(BitpayInsight):
    supported_cryptos = ['rdd']
    domain = "http://live.reddcoin.com"


class FTCe(BitpayInsight):
    supported_cryptos = ['ftc']
    domain = "http://block.ftc-c.com"


class CoinTape(Service):
    supported_cryptos = ['btc']

    def get_optimal_fee(self, crypto, tx_bytes):
        url = "http://api.cointape.com/v1/fees/recommended"
        response = self.get_url(url).json()
        return int(response['fastestFee'] * tx_bytes)

class BitGo(Service):
    base_url = "https://www.bitgo.com"
    optimalFeeNumBlocks = 1

    def get_optimal_fee(self, crypto, tx_bytes):
        url = "%s/api/v1/tx/fee?numBlocks=%s" % (self.base_url, self.optimalFeeNumBlocks)
        response = self.get_url(url).json()
        print(response)
        fee_kb = response['feePerKb']
        return int(tx_bytes * fee_kb / 1024)
