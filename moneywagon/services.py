import json
from .core import Service, NoService, NoData, SkipThisService, currency_to_protocol
import arrow

class Bitstamp(Service):
    service_id = 1
    supported_cryptos = ['btc']
    api_homepage = "https://www.bitstamp.net/api/"

    def get_current_price(self, crypto, fiat):
        if fiat.lower() != 'usd':
            raise SkipThisService('Bitstamp only does USD->BTC')

        url = "https://www.bitstamp.net/api/ticker/"
        response = self.get_url(url).json()
        return (float(response['last']), 'bitstamp')


class BlockCypher(Service):
    service_id = 2
    supported_cryptos = ['btc', 'ltc', 'uro']
    api_homepage = "http://dev.blockcypher.com/"

    explorer_address_url = "https://live.blockcypher.com/{crypto}/address/{address}"
    explorer_tx_url = "https://live.blockcypher.com/{crypto}/tx/{txid}"
    explorer_blockhash_url = "https://live.blockcypher.com/{crypto}/block/{blockhash}/"
    explorer_blocknum_url = "https://live.blockcypher.com/{crypto}/block/{blocknum}/"

    base_api_url = "https://api.blockcypher.com/v1/{crypto}"
    json_address_balance_url = base_api_url + "/main/addrs/{address}"
    json_txs_url = json_address_balance_url
    json_unspent_outputs_url = base_api_url + "/main/addrs/{address}?unspentOnly=true"
    json_blockhash_url = base_api_url + "/main/blocks/{blockhash}"
    json_blocknum_url = base_api_url + "/main/blocks/{blocknum}"

    def get_balance(self, crypto, address, confirmations=1):
        url = self.json_address_balance_url.format(address=address, crypto=crypto)
        response = self.get_url(url)
        if confirmations == 0:
            return response.json()['final_balance'] / 1.0e8
        elif confirmations == 1:
            return response.json()['balance'] / 1.0e8
        else:
            raise SkipThisService("Filtering by confirmations only for 0 and 1")

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = self.json_unspent_outputs_url.format(address=address, crypto=crypto)
        utxos = []
        for utxo in self.get_url(url).json()['txrefs']:
            if utxo['confirmations'] < confirmations:
                continue
            utxos.append(dict(
                amount=utxo['value'],
                output="%s:%s" % (utxo['tx_hash'], utxo['tx_output_n']),
                address=address,
            ))
        return utxos

    def get_transactions(self, crypto, address, confirmations=1):
        url = self.json_txs_url.format(address=address, crypto=crypto)
        transactions = []
        for tx in self.get_url(url).json()['txrefs']:
            if utxo['confirmations'] < confirmations:
                continue
            transactions.append(dict(
                date=arrow.get(tx['confirmed']).datetime,
                amount=tx['value'] / 1e8,
                txid=tx['tx_hash'],
                confirmations=utxo['confirmations']
            ))
        return transactions

    def get_optimal_fee(self, crypto, tx_bytes):
        url = "https://api.blockcypher.com/v1/%s/main" % crypto
        fee_kb = self.get_url(url).json()['low_fee_per_kb']
        return int(tx_bytes * fee_kb / 1024.0)


    def get_block(self, crypto, block_hash='', block_number='', latest=False):
        if block_hash:
            url = self.json_blockhash_url.format(blockhash=block_hash, crypto=crypto)
        elif block_number:
            url = self.json_blocknum_url.format(blocknum=block_number, crypto=crypto)

        r = self.get_url(url).json()
        return dict(
            block_number=r['height'],
            confirmations=r['depth'] + 1,
            time=arrow.get(r['received_time']).datetime,
            sent_value=r['total'] / 1e8,
            total_fees=r['fees'] / 1e8,
            #mining_difficulty=r['bits'],
            hash=r['hash'],
            merkle_root=r['mrkl_root'],
            previous_hash=r['prev_block'],
            tx_count=r['n_tx'],
            txids=r['txids']
        )

class BlockSeer(Service):
    """
    This service has no publically documented API, this code was written
    from looking through chrome dev toolbar.
    """
    service_id = 3
    supported_cryptos = ['btc']
    api_homepage = "https://www.blockseer.com/about"

    explorer_address_url = "https://www.blockseer.com/addresses/{address}"
    explorer_tx_url = "https://www.blockseer.com/transactions/{txid}"
    explorer_blocknum_url = "https://www.blockseer.com/blocks/{blocknum}"
    explorer_blockhash_url = "https://www.blockseer.com/blocks/{blockhash}"

    json_address_balance_url = "https://www.blockseer.com/api/addresses/{address}"
    json_txs_url = "https://www.blockseer.com/api/addresses/{address}/transactions?filter=all"

    def get_balance(self, crypto, address, confirmations=1):
        url = self.json_address_balance_url.format(address=address)
        return self.get_url(url).json()['data']['balance'] / 1e8

    def get_transactions(self, crypo, address):
        url = self.json_txs_url.format(address=address)
        transactions = []
        for tx in self.get_url(url).json()['data']['address']['transactions']:
            transactions.append(dict(
                date=arrow.get(tx['time']).datetime,
                amount=tx['delta'] / 1e8,
                txid=tx['hash'],
            ))
        return transactions


class SmartBitAU(Service):
    service_id = 4
    api_homepage = "https://www.smartbit.com.au/api"
    base_url = "https://api.smartbit.com.au/v1/blockchain"
    explorer_address_url = "https://www.smartbit.com.au/address/{address}"
    explorer_tx_url = "https://www.smartbit.com.au/tx/{txid}"
    explorer_blocknum_url = "https://www.smartbit.com.au/block/{blocknum}"
    explorer_blockhash_url = "https://www.smartbit.com.au/block/{blockhash}"

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
    service_id = 5
    supported_cryptos = ['btc', 'ltc', 'ppc', 'mec', 'qrk', 'dgc', 'tbtc']
    api_homepage = "http://blockr.io/documentation/api"

    explorer_address_url = "http://blockr.io/address/info/{address}"
    explorer_tx_url = "http://blockr.io/address/info/{txid}"
    explorer_blockhash_url = "http://blockr.io/block/info/{blockhash}"
    explorer_blocknum_url = "http://blockr.io/block/info/{blocknum}"
    explorer_latest_block = "http://blockr.io/block/info/latest"

    json_address_url = "http://{crypto}.blockr.io/api/v1/address/info/{address}"
    json_txs_url = url = "http://{crypto}.blockr.io/api/v1/address/txs/{address}"
    json_unspent_outputs_url = "http://{crypto}.blockr.io/api/v1/address/unspent/{address}"

    def get_balance(self, crypto, address, confirmations=1):
        url = self.json_address_url.format(address=address, crypto=crypto)
        response = self.get_url(url)
        return response.json()['data']['balance']

    def get_transactions(self, crypto, address, confirmations=1):
        url = self.json_txs_url.format(address=address, crypto=crypto)
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
        url = self.json_unspent_outputs_url.format(address=address, crypto=crypto)
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
            size=int(r['size']),
            hash=r['hash'],
            merkle_root=r['merkleroot'],
            previous_hash=r['prev_block_hash'],
            next_hash=r['next_block_hash'],
            tx_count=r['nb_txs'],
        )


class Toshi(Service):
    api_homepage = "https://toshi.io/docs/"
    service_id = 6
    url = "https://bitcoin.toshi.io/api/v0"

    supported_cryptos = ['btc']

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/addresses/%s" % (self.url, address)
        response = self.get_url(url).json()
        return response['balance'] / 1e8

    def get_transactions(self, crypto, address, confirmations=1):
        url = "%s/addresses/%s/transactions" % (self.url, address)
        response = self.get_url(url).json()

        if confirmations == 0:
            to_iterate = response['transactions'] + response['unconfirmed_transactions']
        else:
            to_iterate = response['transactions']

        transactions = []
        for tx in to_iterate:
            if tx['confirmations'] < confirmations:
                continue
            transactions.append(dict(
                amount=sum([x['amount'] / 1e8 for x in tx['outputs'] if address in x['addresses']]),
                txid=tx['hash'],
                date=arrow.get(tx['block_time']).datetime,
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
                confirmations=cons
            ))
        return utxos


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
    service_id = 7
    api_homepage = "https://btc-e.com/api/documentation"

    def get_current_price(self, crypto, fiat):
        pair = "%s_%s" % (crypto.lower(), fiat.lower())
        url = "https://btc-e.com/api/3/ticker/" + pair
        response = self.get_url(url).json()
        return (response[pair]['last'], 'btc-e')


class Cryptonator(Service):
    service_id = 8
    api_homepage = "https://www.cryptonator.com/api"

    def get_current_price(self, crypto, fiat):
        pair = "%s-%s" % (crypto, fiat)
        url = "https://www.cryptonator.com/api/ticker/%s" % pair
        response = self.get_url(url).json()
        return float(response['ticker']['price']), 'cryptonator'


class Winkdex(Service):
    service_id = 9
    supported_cryptos = ['btc']
    api_homepage = "http://docs.winkdex.com/"

    def get_current_price(self, crypto, fiat):
        if fiat != 'usd':
            raise SkipThisService("winkdex is btc->usd only")
        url = "https://winkdex.com/api/v0/price"
        return self.get_url(url).json()['price'] / 100.0, 'winkdex'


class ChainSo(Service):
    service_id = 11
    api_homepage = "https://chain.so/api"
    base_url = "https://chain.so/api/v2"
    explorer_address_url = "https://chain.so/address/{crypto}/{address}"
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
    service_id = 12
    api_homepage = "http://docs.coinprism.apiary.io/"
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
    service_id = 13
    api_homepage = "https://support.biteasy.com/kb"
    supported_cryptos = ['btc']
    explorer_address_url = "https://www.biteasy.com/blockchain/addresses/{address}"
    explorer_tx_url = "https://www.biteasy.com/blockchain/transactions/{txid}"
    explorer_blockhash_url = "https://www.biteasy.com/blockchain/blocks/{blockhash}"

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://api.biteasy.com/blockchain/v1/addresses/" + address
        response = self.get_url(url)
        return response.json()['data']['balance'] / 1e8


class BlockChainInfo(Service):
    service_id = 14
    api_homepage = "https://blockchain.info/api"
    supported_cryptos = ['btc']
    explorer_address_url = "https://blockchain.info/address/{address}"
    explorer_tx_url = "https://blockchain.info/tx/{txid}"
    explorer_blocknum_url = "https://blockchain.info/block-index/{blocknum}"
    explorer_blockhash_url = "https://blockchain.info/block/{blockhash}"

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://blockchain.info/address/%s?format=json" % address
        response = self.get_url(url)
        return float(response.json()['final_balance']) * 1e-8

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = "https://blockchain.info/unspent?active=%s" % address

        response = self.get_url(url)
        if response.content == 'No free outputs to spend':
            return []

        utxos = []
        for utxo in response.json()['unspent_outputs']:
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
    service_id = 15
    supported_cryptos = ['btc']
    base_url = "http://bitcoin-abe.info/chain/Bitcoin"
    # decomissioned, kept here because other services need it as base class

    def get_balance(self, crypto, address, confirmations=1):
        url = self.base_url + "/q/addressbalance/" + address
        response = self.get_url(url)
        return float(response.content)


class DogeChainInfo(BitcoinAbe):
    service_id = 18
    supported_cryptos = ['doge']
    base_url = "https://dogechain.info/chain/Dogecoin"
    api_homepage = "https://dogechain.info/api"


class AuroraCoinEU(BitcoinAbe):
    service_id = 19
    supported_cryptos = ['aur']
    base_url = 'http://blockexplorer.auroracoin.eu/chain/AuroraCoin'


class Atorox(BitcoinAbe):
    service_id = 20
    supported_cryptos = ['aur']
    base_url = "http://auroraexplorer.atorox.net/chain/AuroraCoin"

##################################

class FeathercoinCom(Service):
    service_id = 21
    supported_cryptos = ['ftc']
    api_homepage = "http://api.feathercoin.com/"

    def get_balance(self, crypto, address, confirmations=1):
        url= "http://api.feathercoin.com/?output=balance&address=%s&json=1" % address
        response = self.get_url(url)
        return float(response.json()['balance'])


class NXTPortal(Service):
    service_id = 22
    supported_cryptos = ['nxt']
    api_homepage = "https://nxtportal.org/"

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
    service_id = 23
    api_homepage = "https://chainz.cryptoid.info/api.dws"

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
    service_id = 24
    api_homepage = "https://cryptap.us/"
    supported_cryptos = [
        'nmc', 'wds', 'ber', 'scn', 'sc0', 'wdc', 'nvc', 'cas', 'myr'
    ]

    def get_balance(self, crypto, address, confirmations=1):
        url = "http://cryptap.us/%s/explorer/q/addressbalance/%s" % (crypto, address)
        return float(self.get_url(url).content)


class BTER(Service):
    service_id = 25
    api_homepage = "https://bter.com/api"

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

################################################

class BitpayInsight(Service):
    service_id = 28
    supported_cryptos = ['btc']
    domain = "http://insight.bitpay.com"
    api_homepage = domain + "/api"
    explorer_address_url = "https://insight.bitpay.com/address/{address}"


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
    service_id = 29
    supported_cryptos = ['btc']
    domain = "http://insight.thebit.info"
    api_homepage = domain + "/api"


class MYRCryptap(BitpayInsight):
    service_id = 30
    supported_cryptos = ['myr']
    domain = "http://insight-myr.cryptap.us"
    api_homepage = domain + "/api"


class BirdOnWheels(BitpayInsight):
    service_id = 31
    supported_cryptos = ['myr']
    domain = "http://birdonwheels5.no-ip.org:3000"
    api_homepage = domain + "/api"


class ThisIsVTC(BitpayInsight):
    service_id = 32
    supported_cryptos = ['vtc']
    domain = "http://explorer.thisisvtc.com"
    api_homepage = domain + "/api"


class ReddcoinCom(BitpayInsight):
    service_id = 33
    supported_cryptos = ['rdd']
    domain = "http://live.reddcoin.com"
    api_homepage = domain + "/api"


class FTCe(BitpayInsight):
    service_id = 34
    supported_cryptos = ['ftc']
    domain = "http://block.ftc-c.com"
    api_homepage = domain + "/api"


class CoinTape(Service):
    service_id = 35
    api_homepage = "http://api.cointape.com/api"
    supported_cryptos = ['btc']

    def get_optimal_fee(self, crypto, tx_bytes):
        url = "http://api.cointape.com/v1/fees/recommended"
        response = self.get_url(url).json()
        return int(response['fastestFee'] * tx_bytes)

class BitGo(Service):
    service_id = 36
    api_homepage = 'https://www.bitgo.com/api/'

    base_url = "https://www.bitgo.com"
    optimalFeeNumBlocks = 1
    supported_cryptos = ['btc']

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/api/v1/address/%s" % (self.base_url, address)
        response = self.get_url(url).json()
        if confirmations == 0:
            return response['balance'] / 1e8
        if confirmations == 1:
            return response['confirmedBalance'] / 1e8
        else:
            raise SkipThisService('Filtering by confirmation only available for 0 or 1')

    def get_transactions(self, crypto, address):
        url = "%s/api/v1/address/%s/tx" % (self.base_url, address)
        response = self.get_url(url).json()

        txs = []
        for tx in response['transactions']:
            my_outs = [x['value'] for x in tx['entries'] if x['account'] == address]

            txs.append(dict(
                amount=sum(my_outs),
                date=arrow.get(tx['date']).datetime,
                txid=tx['id'],
                confirmations=tx['confirmations'],
            ))
        return txs

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = "%s/api/v1/address/%s/unspents" % (self.base_url, address)
        utxos = []
        for utxo in self.get_url(url).json()['unspents']:
            utxos.append(dict(
                output="%s:%s" % (utxo['tx_hash'], utxo['tx_output_n']),
                amount=utxo['value'],
                confirmations=utxo['confirmations'],
                address=address
            ))
        return utxos

    def get_block(self, crypto, block_number='', block_hash='', latest=False):
        if latest:
            url = "/api/v1/block/latest"
        else:
            url = "/api/v1/block/" + block_number + block_hash

        r = self.get_url(self.base_url + url)
        return dict(
            block_number=r['height'],
            time=arrow.get(r['date']).datetime,
            hash=r['id'],
            previous_hash=r['previous'],
            txids=r['transactions'],
            tx_count=len(r['transactions'])
        )

    def get_optimal_fee(self, crypto, tx_bytes):
        url = "%s/api/v1/tx/fee?numBlocks=%s" % (self.base_url, self.optimalFeeNumBlocks)
        response = self.get_url(url).json()
        fee_kb = response['feePerKb']
        return int(tx_bytes * fee_kb / 1024)

class Blockonomics(Service):
    service_id = 37
    supported_cryptos = ['btc']
    api_homepage = "https://www.blockonomics.co/views/api.html"

    def get_balance(self, crypto, address, confirmations=1):
        return self.get_balance_multi(crypto, [address], confirmations)[address]

    def get_balance_multi(self, crypto, addresses, confirmations=1):
        url = "https://www.blockonomics.co/api/balance"
        response = self.post_url(url, json.dumps({'addr': ' '.join(addresses)})).json()
        balances = {}
        for data in response['response']:
            confirmed = data['confirmed'] / 1e8
            if confirmations == 0:
                balance = confirmed + (data['unconfirmed'] / 1e8)
            if confirmations == 1:
                balance = confirmed
            else:
                raise SkipThisService("Can't filter by confirmations")

            balances[data['addr']] = balance

        return balances

    def get_transactions(self, crypto, address):
        url = "https://www.blockonomics.co/api/searchhistory"
        response = self.post_url(url, json.dumps({'addr': address})).json()
        txs = []
        for tx in response['history']:
            txs.append(dict(
                amount=tx['value'] / 1e8,
                date=arrow.get(tx['time']).datetime,
                txid=tx['txid'],
            ))
        return txs

class BlockExplorerCom(BitpayInsight):
    service_id = 38
    supported_cryptos = ['btc']
    domain = "https://blockexplorer.com"
    api_homepage = domain + "/api"
