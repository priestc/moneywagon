import json
from .core import Service, NoService, NoData, SkipThisService, currency_to_protocol
import arrow

class Bitstamp(Service):
    service_id = 1
    supported_cryptos = ['btc']
    api_homepage = "https://www.bitstamp.net/api/"
    name = "Bitstamp"

    def get_current_price(self, crypto, fiat):
        if fiat.lower() != 'usd':
            raise SkipThisService('Bitstamp only does USD->BTC')

        url = "https://www.bitstamp.net/api/ticker/"
        response = self.get_url(url).json()
        return float(response['last'])


class BlockCypher(Service):
    service_id = 2
    supported_cryptos = ['btc', 'ltc', 'doge']
    api_homepage = "http://dev.blockcypher.com/"

    explorer_address_url = "https://live.blockcypher.com/{crypto}/address/{address}"
    explorer_tx_url = "https://live.blockcypher.com/{crypto}/tx/{txid}"
    explorer_blockhash_url = "https://live.blockcypher.com/{crypto}/block/{blockhash}/"
    explorer_blocknum_url = "https://live.blockcypher.com/{crypto}/block/{blocknum}/"

    base_api_url = "https://api.blockcypher.com/v1/{crypto}"
    json_address_balance_url = base_api_url + "/main/addrs/{address}"
    json_txs_url = json_address_balance_url
    json_unspent_outputs_url = base_api_url + "/main/addrs/{address}/full?unspentOnly=true&includeScript=true"
    json_blockhash_url = base_api_url + "/main/blocks/{blockhash}"
    json_blocknum_url = base_api_url + "/main/blocks/{blocknum}"
    name = "BlockCypher"

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
        for utxo in self.get_url(url).json()['txs']:
            if utxo['confirmations'] < confirmations:
                continue
            for n, output in enumerate(utxo['outputs']):
                output_addrs = output['addresses']
                if address in output_addrs and len(output_addrs) == 1:
                    utxos.append(dict(
                        txid=utxo['hash'],
                        amount=output['value'],
                        output="%s:%s" % (utxo['hash'], n),
                        vout=n,
                        scriptPubKey=output['script'],
                        address=address,
                        confirmations=utxo['confirmations'],
                    ))
                elif address in output_addrs:
                    raise Exception("Multisig not implemented yet")

        return utxos

    def get_transactions(self, crypto, address, confirmations=1):
        url = self.json_txs_url.format(address=address, crypto=crypto)
        transactions = []
        for tx in self.get_url(url).json().get('txrefs', []):
            if tx['confirmations'] < confirmations:
                continue
            transactions.append(dict(
                date=arrow.get(tx['confirmed']).datetime,
                amount=tx['value'] / 1e8,
                txid=tx['tx_hash'],
                confirmations=tx['confirmations']
            ))
        return transactions

    def get_single_transaction(self, crypto, txid):
        url = "https://api.blockcypher.com/v1/%s/main/txs/%s" % (crypto, txid)
        tx = self.get_url(url).json()
        ins = [{'address': x['addresses'][0], 'amount': x['output_value']} for x in tx['inputs']]
        outs = [{'address': x['addresses'][0], 'amount': x['value']} for x in tx['outputs']]

        return dict(
            txid=txid,
            confirmations=tx['confirmations'],
            size=tx['size'],
            time=arrow.get(tx['received']).datetime,
            block_hash=tx['block_hash'],
            block_number=tx['block_height'],
            inputs=ins,
            outputs=outs,
            total_in=sum(x['amount'] for x in ins),
            total_out=sum(x['amount'] for x in ins),
            fees=tx['fees'],
        )

    def get_optimal_fee(self, crypto, tx_bytes):
        url = "https://api.blockcypher.com/v1/%s/main" % crypto
        fee_kb = self.get_url(url).json()['high_fee_per_kb']
        return int(tx_bytes * fee_kb / 1024.0)


    def get_block(self, crypto, block_hash='', block_number='', latest=False):
        if block_number == 0:
            raise SkipThisService("BlockCypher does not support block #0")

        if block_hash:
            url = self.json_blockhash_url.format(blockhash=block_hash, crypto=crypto)
        elif block_number != '':
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
    name = "BlockSeer"

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
    name = "SmartBit"

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
                txid=utxo['txid'],
                vout=utxo['n'],
                confirmations=utxo['confirmations'],
                scriptPubKey=utxo['script_pub_key']['hex'],
                scriptPubKey_asm=utxo['script_pub_key']['asm']
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
    json_single_tx_url = "http://{crypto}.blockr.io/api/v1/tx/info/{txid}"
    json_txs_url = url = "http://{crypto}.blockr.io/api/v1/address/txs/{address}"
    json_unspent_outputs_url = "http://{crypto}.blockr.io/api/v1/address/unspent/{address}"
    name = "Blockr.io"

    def get_balance(self, crypto, address, confirmations=1):
        url = self.json_address_url.format(address=address, crypto=crypto)
        response = self.get_url(url)
        return response.json()['data']['balance']

    def get_balance_multi(self, crypto, addresses, confirmations=1):
        url = self.json_address_url.format(address=','.join(addresses), crypto=crypto)
        balances = {}
        for bal in self.get_url(url).json()['data']:
            balances[bal['address']] = bal['balance']
        return balances

    def _format_tx(self, tx, address):
        return dict(
            date=arrow.get(tx['time_utc']).datetime,
            amount=tx['amount'],
            txid=tx['tx'],
            confirmations=tx['confirmations'],
            addresses=[address],
        )

    def get_transactions(self, crypto, address, confirmations=1):
        url = self.json_txs_url.format(address=address, crypto=crypto)
        response = self.get_url(url)

        transactions = []
        for tx in response.json()['data']['txs']:
            transactions.append(self._format_tx(tx, address))
        return transactions

    def get_transactions_multi(self, crypto, addresses, confirmation=1):
        url = self.json_txs_url.format(address=','.join(addresses), crypto=crypto)
        transactions = []
        for data in self.get_url(url).json()['data']:
            for tx in data['txs']:
                transactions.append(self._format_tx(tx, data['address']))
        return transactions

    def _format_single_tx(self, tx):
        ins = [{'address': x['address'], 'amount': float(x['amount']) * -1} for x in tx['vins']]
        outs = [{'address': x['address'], 'amount': float(x['amount'])} for x in tx['vouts']]

        return dict(
            time=arrow.get(tx['time_utc']).datetime,
            block_number=tx['block'],
            inputs=ins,
            outputs=outs,
            txid=tx['tx'],
            total_in=sum(x['amount'] for x in ins),
            total_out=sum(x['amount'] for x in outs),
            confirmations=tx['confirmations'],
            fee=float(tx['fee'])
        )

    def get_single_transaction(self, crypto, txid):
        url = self.json_single_tx_url.format(crypto=crypto, txid=txid)
        r = self.get_url(url).json()['data']
        return self._format_single_tx(r)


    def get_single_transaction_multi(self, crypto, txids):
        url = self.json_single_tx_url.format(crypto=crypto, txid=','.join(txids))
        txs = []
        for tx in self.get_url(url).json()['data']:
            txs.append(self._format_single_tx(tx))
        return txs

    def _format_utxo(self, utxo, address):
        return dict(
            amount=currency_to_protocol(utxo['amount']),
            address=address,
            output="%s:%s" % (utxo['tx'], utxo['n']),
            txid=utxo['tx'],
            vout=utxo['n'],
            confirmations=utxo['confirmations'],
            scriptPubKey=utxo['script']
        )

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = self.json_unspent_outputs_url.format(address=address, crypto=crypto)
        utxos = []
        for utxo in self.get_url(url).json()['data']['unspent']:
            cons = utxo['confirmations']
            if cons < confirmations:
                continue
            utxos.append(self._format_utxo(utxo, address))
        return utxos

    def get_unspent_outputs_multi(self, crypto, addresses, confirmations=1):
        url = self.json_unspent_outputs_url.format(address=','.join(addresses), crypto=crypto)
        utxos = []
        for data in self.get_url(url).json()['data']:
            for utxo in data['unspent']:
                cons = utxo['confirmations']
                if cons < confirmations:
                    continue
                utxos.append(self._format_utxo(utxo, data['address']))
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
        if block_number == 0:
            raise SkipThisService("Block 0 not supported (bug in Blockr.io?)")

        url ="http://%s.blockr.io/api/v1/block/info/%s%s%s" % (
            crypto,
            block_hash if block_hash != '' else '',
            block_number if block_number != '' else '',
            'last' if latest else ''
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
    name = "Toshi"

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


class BTCE(Service):
    service_id = 7
    api_homepage = "https://btc-e.com/api/documentation"
    name = "BTCe"

    def get_current_price(self, crypto, fiat):
        pair = "%s_%s" % (crypto.lower(), fiat.lower())
        url = "https://btc-e.com/api/3/ticker/" + pair
        response = self.get_url(url).json()
        return response[pair]['last']


class Cryptonator(Service):
    service_id = 8
    api_homepage = "https://www.cryptonator.com/api"
    name = "Cryptonator"

    def get_current_price(self, crypto, fiat):
        pair = "%s-%s" % (crypto, fiat)
        url = "https://www.cryptonator.com/api/ticker/%s" % pair
        response = self.get_url(url).json()
        return float(response['ticker']['price'])


class Winkdex(Service):
    service_id = 9
    supported_cryptos = ['btc']
    api_homepage = "http://docs.winkdex.com/"
    name = "Winkdex"

    def get_current_price(self, crypto, fiat):
        if fiat != 'usd':
            raise SkipThisService("winkdex is btc->usd only")
        url = "https://winkdex.com/api/v0/price"
        return self.get_url(url).json()['price'] / 100.0,


class ChainSo(Service):
    service_id = 11
    api_homepage = "https://chain.so/api"
    base_url = "https://chain.so/api/v2"
    explorer_address_url = "https://chain.so/address/{crypto}/{address}"
    supported_cryptos = ['doge', 'btc', 'ltc']
    name = "Chain.So"

    def get_current_price(self, crypto, fiat):
        url = "%s/get_price/%s/%s" % (self.base_url, crypto, fiat)
        resp = self.get_url(url).json()
        items = resp['data']['prices']
        if len(items) == 0:
            raise SkipThisService("Chain.so can't get price for %s/%s" % (crypto, fiat))

        self.name = "%s via Chain.so" % items[0]['exchange']
        return float(items[0]['price'])

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
                confirmations=utxo['confirmations'],
                txid=utxo['txid'],
                vout=utxo['output_no'],
                scriptPubKey=utxo['script_hex'],
                scriptPubKey_asm=utxo['script_asm'],
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
    name = "CoinPrism"

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
                    confirmations=tx['confirmations'],
                    txid=tx['transaction_hash'],
                    vout=tx['output_index'],
                    scriptPubKey=utxo['script_hex'],
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
    name = "BitEasy"

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://api.biteasy.com/blockchain/v1/addresses/" + address
        response = self.get_url(url)
        return response.json()['data']['balance'] / 1e8


class BlockChainInfo(Service):
    service_id = 14
    domain = "blockchain.info"
    api_homepage = "https://{domain}/api"
    supported_cryptos = ['btc']
    explorer_address_url = "https://{domain}/address/{address}"
    explorer_tx_url = "https://{domain}/tx/{txid}"
    explorer_blocknum_url = "https://{domain}/block-index/{blocknum}"
    explorer_blockhash_url = "https://{domain}/block/{blockhash}"
    name = "Blockchain.info"

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://%s/address/%s?format=json" % (self.domain, address)
        response = self.get_url(url)
        return float(response.json()['final_balance']) * 1e-8

    def get_single_transaction(self, crypto, txid):
        url = "https://%s/tx-index/%s?format=json" % (
            self.domain, txid
        )
        tx = self.get_url(url).json()
        outs = [{'address': x['addr'], 'amount': float(x['value']) / 1e8} for x in tx['out']]
        ins = []
        for in_ in tx['inputs']:
            if 'prev_out' in in_:
                prev = in_['prev_out']
                ins.append(
                    {'address': prev['addr'], 'amount': float(prev['value']) / 1e8}
                )

        return dict(
            txid=txid,
            block_number=tx.get('block_height', None),
            size=tx['size'],
            time=arrow.get(tx['time']).datetime,
            inputs=ins,
            outputs=outs,
            total_in=sum(x['amount'] for x in ins),
            total_out=sum(x['amount'] for x in outs),
        )


    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = "https://%s/unspent?active=%s" % (self.domain, address)

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
                txid=utxo['tx_hash_big_endian'],
                vout=utxo['tx_output_n'],
                confirmations=utxo['confirmations'],
                scriptPubKey=utxo['script'],
            ))
        return utxos


##################################

class BitcoinAbe(Service):
    service_id = 15
    supported_cryptos = ['btc']
    base_url = "http://bitcoin-abe.info/chain/Bitcoin"
    name = "Abe"
    # decomissioned, kept here because other services need it as base class

    def get_balance(self, crypto, address, confirmations=1):
        url = self.base_url + "/q/addressbalance/" + address
        response = self.get_url(url)
        return float(response.content)


class DogeChainInfo(Service):
    service_id = 18
    supported_cryptos = ['doge']
    base_url = "https://dogechain.info/chain/Dogecoin"
    api_homepage = "https://dogechain.info/api/blockchain_api"
    name = "DogeChain.info"

    def get_balance(self, crypto, address, confirmations):
        url = "https://dogechain.info/api/v1/address/balance/" + address
        response = self.get_url(url).json()
        return response['balance']

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = "https://dogechain.info/api/v1/unspent/" + address
        response = self.get_url(url).json()
        utxos = []
        for utxo in response['unspent_outputs']:
            utxos.append(dict(
                confirmations=utxo['confirmations'],
                amount=int(utxo['value']),
                scriptPubKey=utxo['script'],
                vout=utxo['tx_output_n'],
                txid=utxo['tx_hash'],
                output="%s:%s" % (utxo['tx_hash'], utxo['tx_output_n'])
            ))
        return utxos

    def get_single_transaction(self, crypto, txid):
        url = "https://dogechain.info/api/v1/transaction/" + txid
        tx = self.get_url(url).json()['transaction']
        return dict(
            txid=txid,
            confirmations=tx['confirmations'],
            size=tx['size'],
            time=arrow.get(r['time']).datetime,
            block_hash=r['block_hash'],
            inputs=[{'address': x['address'], 'amount': float(x['value'])} for x in r['inputs']],
            outputs=[{'address': x['address'], 'amount': float(x['value'])} for x in r['outputs']],
            total_in=r['total_input'],
            total_out=r['total_output'],
        )


class AuroraCoinEU(BitcoinAbe):
    service_id = 19
    supported_cryptos = ['aur']
    base_url = 'http://blockexplorer.auroracoin.eu/chain/AuroraCoin'
    name = "AuroraCoin.eu"


class Atorox(BitcoinAbe):
    service_id = 20
    supported_cryptos = ['aur']
    base_url = "http://auroraexplorer.atorox.net/chain/AuroraCoin"
    name = "atorox.net"

##################################

class FeathercoinCom(Service):
    service_id = 21
    supported_cryptos = ['ftc']
    api_homepage = "http://api.feathercoin.com/"
    name = "Feathercoin.com"

    def get_balance(self, crypto, address, confirmations=1):
        url= "http://api.feathercoin.com/?output=balance&address=%s&json=1" % address
        response = self.get_url(url)
        return float(response.json()['balance'])


class NXTPortal(Service):
    service_id = 22
    supported_cryptos = ['nxt']
    api_homepage = "https://nxtportal.org/"
    name = "NXT Portal"

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
    name = "CryptoID"
    api_key = "bc1063f00936"

    supported_cryptos = [
        'dash', 'bc', 'bay', 'block', 'cann', 'uno', 'vrc', 'xc', 'uro', 'aur',
        'pot', 'cure', 'arch', 'swift', 'karm', 'dgc', 'lxc', 'sync', 'byc',
        'pc', 'fibre', 'i0c', 'nobl', 'gsx', 'flt', 'ccn', 'rlc', 'rby', 'apex',
        'vior', 'ltcd', 'zeit', 'carbon', 'super', 'dis', 'ac', 'vdo', 'ioc',
        'xmg', 'cinni', 'crypt', 'excl', 'mne', 'seed', 'qslv', 'maryj', 'key',
        'oc', 'ktk', 'voot', 'glc', 'drkc', 'mue', 'gb', 'piggy', 'jbs', 'grs',
        'icg', 'rpc', 'tx'
    ]

    def get_balance(self, crypto, address, confirmations=1):
        url = "http://chainz.cryptoid.info/%s/api.dws?q=getbalance&a=%s&key=%s" % (
            crypto, address, self.api_key
        )
        return float(self.get_url(url).content)

    def get_single_transaction(self, crypto, txid):
        url = "http://chainz.cryptoid.info/%s/api.dws?q=txinfo&t=%s&key=%s" % (
            crypto, txid, self.api_key
        )
        r = self.get_url(url).json()

        return dict(
            time=arrow.get(r['timestamp']).datetime,
            block_number=r['block'],
            inputs=[{'address': x['addr'], 'amount': x['amount']} for x in r['inputs']],
            outputs=[{'address': x['addr'], 'amount': x['amount']} for x in r['outputs']],
            txid=txid,
            total_in=r['total_input'],
            total_out=r['total_output'],
            confirmations=r['confirmations'],
        )

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = "http://chainz.cryptoid.info/%s/api.dws?q=unspent&active=%s&key=%s" % (
            crypto, address, self.api_key
        )

        resp = self.get_url(url)
        if resp.status_code != 200:
            raise Exception("CryptoID returned Error: %s" % resp.content)

        ret = []
        for utxo in resp.json()['unspent_outputs']:
            ret.append(dict(
                output="%s:%s" % (utxo['tx_hash'], utxo['tx_ouput_n']),
                amount=int(utxo['value']),
                confirmations=utxo['confirmations'],
                address=address,
                txid=utxo['tx_hash'],
                vout=utxo['tx_ouput_n'],
            ))
        return ret


class CryptapUS(Service):
    service_id = 24
    api_homepage = "https://cryptap.us/"
    name = "cryptap.us"
    supported_cryptos = [
        'nmc', 'wds', 'ber', 'scn', 'sc0', 'wdc', 'nvc', 'cas', 'myr'
    ]

    def get_balance(self, crypto, address, confirmations=1):
        url = "http://cryptap.us/%s/explorer/q/addressbalance/%s" % (crypto, address)
        return float(self.get_url(url).content)


class BTER(Service):
    service_id = 25
    api_homepage = "https://bter.com/api"
    name = "BTER"

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

            self.name = 'BTER (calculated)'

            return (btc_fiat * altcoin_btc)

        return float(response['last'] or 0)

################################################

class BitpayInsight(Service):
    service_id = 28
    supported_cryptos = ['btc']
    domain = "insight.bitpay.com"
    protocol = 'https'
    api_homepage = "{protocol}://{domain}/api"
    explorer_address_url = "{protocol}://{domain}/address/{address}"

    name = "Bitpay Insight"

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s://%s/api/addr/%s/balance" % (self.protocol, self.domain, address)
        return float(self.get_url(url).content) / 1e8

    def _format_tx(self, tx, addresses):
        matched_addresses = []
        my_outs = 0
        my_ins = 0
        for address in addresses:
            for x in tx['vout']:
                if address in x['scriptPubKey']['addresses']:
                    my_outs += float(x['value'])
                    matched_addresses.append(address)
            for x in tx['vin']:
                if address in x['addr']:
                    my_ins += float(x['value'])
                    matched_addresses.append(address)

        return dict(
            amount=my_outs - my_ins,
            date=arrow.get(tx['time']).datetime,
            txid=tx['txid'],
            confirmations=tx['confirmations'],
            addresses=list(set(matched_addresses))
        )

    def get_transactions(self, crypto, address):
        url = "%s://%s/api/txs/?address=%s" % (self.protocol, self.domain, address)
        response = self.get_url(url)
        transactions = []
        for tx in response.json()['txs']:
            transactions.append(self._format_tx(tx, [address]))
        return transactions

    def get_transactions_multi(self, crypto, addresses):
        url = "%s://%s/api/addrs/%s/txs" % (self.protocol, self.domain, ','.join(addresses))
        r = self.get_url(url).json()
        txs = []
        for tx in r['items']:
            txs.append(self._format_tx(tx, addresses))
        return txs

    def get_single_transaction(self, crypto, txid):
        url = "%s://%s/api/tx/%s" % (self.protocol, self.domain, txid)
        d = self.get_url(url).json()
        return dict(
            time=arrow.get(d['blocktime']).datetime,
            confirmations=d['confirmations'],
            total_in=float(d['valueIn']),
            total_out=float(d['valueOut']),
            fee=d['fees'],
            inputs=[{'address': x['addr'], 'value': x['value']} for x in d['vin']],
            outputs=[{'address': x['scriptPubKey']['addresses'][0], 'value': x['value']} for x in d['vout']],
            txid=txid,
        )

    def _format_utxo(self, utxo):
        return dict(
            txid=utxo['txid'],
            vout=utxo['vout'],
            scriptPubKey=utxo['scriptPubKey'],
            output="%s:%s" % (utxo['txid'], utxo['vout']),
            amount=currency_to_protocol(utxo['amount']),
            confirmations=utxo['confirmations'],
            address=utxo['address']
        )

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = "%s://%s/api/addr/%s/utxo?noCache=1" % (self.protocol, self.domain, address)
        utxos = []
        for utxo in self.get_url(url).json():
            utxos.append(self._format_utxo(utxo))
        return utxos

    def get_unspent_outputs_multi(self, crypto, addresses, confirmations=1):
        url = "%s://%s/api/addrs/%s/utxo?noCache=1" % (self.protocol, self.domain, ','.join(addresses))
        utxos = []
        for utxo in self.get_url(url).json():
            utxos.append(self._format_utxo(utxo))
        return utxos

    def get_block(self, crypto, block_number='', block_hash='', latest=False):

        if latest:
            url = "%s://%s/api/status?q=getLastBlockHash" % (self.protocol, self.domain)
            block_hash = self.get_url(url).json()['lastblockhash']

        elif block_number != '':
            url = "%s://%s/api/block-index/%s" % (self.protocol, self.domain, block_number)
            block_hash = self.get_url(url).json()['blockHash']

        url = "%s://%s/api/block/%s" % (self.protocol, self.domain, block_hash)

        r = self.get_url(url).json()
        return dict(
            block_number=r['height'],
            version=r['version'],
            confirmations=r['confirmations'],
            time=arrow.get(r['time']).datetime,
            mining_difficulty=float(r['difficulty']),
            size=r['size'],
            hash=r['hash'],
            merkle_root=r['merkleroot'],
            previous_hash=r.get('previousblockhash', None),
            next_hash=r.get('nextblockhash', None),
            txids=r['tx'],
            tx_count=len(r['tx'])
        )

    def push_tx(self, crypto, tx_hex):
        url = "%s://%s/api/tx/send" % (self.protocol, self.domain)
        return self.post_url(url, {'rawtx': tx_hex}).json()['txid']


    def get_optimal_fee(self, crypto, tx_bytes):
        url = "%s://%s/api/utils/estimatefee?nbBlocks=2" % (self.protocol, self.domain)
        return self.get_url(url).json()

class MYRCryptap(BitpayInsight):
    service_id = 30
    protocol = 'http'
    supported_cryptos = ['myr']
    domain = "insight-myr.cryptap.us"
    name = "MYR cryptap"


class BirdOnWheels(BitpayInsight):
    service_id = 31
    supported_cryptos = ['myr']
    domain = "birdonwheels5.no-ip.org:3000"
    name = "Bird on Wheels"


class ThisIsVTC(BitpayInsight):
    service_id = 32
    supported_cryptos = ['vtc']
    domain = "explorer.thisisvtc.com"
    name = "This is VTC"


class ReddcoinCom(BitpayInsight):
    service_id = 33
    supported_cryptos = ['rdd']
    domain = "live.reddcoin.com"
    name = "Reddcoin.com"


class CoinTape(Service):
    service_id = 35
    api_homepage = "http://api.cointape.com/api"
    supported_cryptos = ['btc']
    base_url = "http://api.cointape.com"
    name = "CoinTape"

    def get_optimal_fee(self, crypto, tx_bytes):
        url = self.base_url + "/v1/fees/recommended"
        response = self.get_url(url).json()
        return int(response['fastestFee'] * tx_bytes)

class BitGo(Service):
    service_id = 36
    api_homepage = 'https://www.bitgo.com/api/'
    name = "BitGo"

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
                address=address,
                script=utxo['script'],
                vout=utxo['tx_output_n'],
            ))
        return utxos

    def get_block(self, crypto, block_number='', block_hash='', latest=False):
        if block_number == 0:
            raise SkipThisService("Block #0 broken for this service")

        if latest:
            url = "/api/v1/block/latest"
        elif block_number != '':
            url = "/api/v1/block/%s" % block_number
        else:
            url = "/api/v1/block/%s" % block_hash

        r = self.get_url(self.base_url + url).json()
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
    name = "Blockonomics"
    base_url = "https://www.blockonomics.co"
    def get_balance(self, crypto, address, confirmations=1):
        return self.get_balance_multi(crypto, [address], confirmations)[address]

    def get_balance_multi(self, crypto, addresses, confirmations=1):
        url = "%s/api/balance" % self.base_url

        if hasattr(addresses, 'startswith') and addresses.startswith("xpub"):
            body = {'addr': addresses}
        else:
            body = {'addr': ' '.join(addresses)}

        response = self.post_url(url, json.dumps(body)).json()
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
        url = "%s/api/searchhistory" % self.base_url
        response = self.post_url(url, json.dumps({'addr': address})).json()
        txs = []
        for tx in response['history']:
            txs.append(dict(
                amount=tx['value'] / 1e8,
                date=arrow.get(tx['time']).datetime,
                txid=tx['txid'],
            ))
        return txs

    def get_single_transaction(self, crypto, txid):
        url = "%s/api/tx_detail?txid=%s" % (self.base_url, txid)
        d = self.get_url(url).json()
        return dict(
            time=arrow.get(d['time']).datetime,
            inputs=[{'address': x['address'], 'value': x['value'] / 1e8} for x in d['vin']],
            outputs=[{'address': x['address'], 'value': x['value']/ 1e8} for x in d['vout']],
            txid=txid,
            fees=d['fee']/1e8,
            size=d['size']
        )


class BlockExplorerCom(BitpayInsight):
    service_id = 38
    supported_cryptos = ['btc']
    domain = "blockexplorer.com"
    name = "BlockExplorer.com"

class BitNodes(Service):
    domain = "https://bitnodes.21.co"
    service_id = 39
    name = "Bitnodes.21.co"

    def get_nodes(self, crypto):
        response = self.get_url(self.domain + "/api/v1/snapshots/latest/")
        nodes_dict = response.json()['nodes']

        nodes = []
        for address, data in nodes_dict.items():
            nodes.append({
                'address': address,
                'protocol_version': data[0],
                'user_agent': data[1],
                'connected_since': arrow.get(data[2]).datetime,
                'services': data[3],
                'height': data[4],
                'hostname': data[5],
                'city': data[6],
                'country': data[7],
                'latitude': data[8],
                'longitude': data[9],
                'timezone': data[10],
                'asn': data[11],
                'organization': data[12]
            })

        return nodes

class BitcoinFees21(CoinTape):
    base_url = "https://bitcoinfees.21.co/api"
    service_id = 40
    name = "bitcoinfees.21.co"
    api_homepage = "https://bitcoinfees.21.co/api"
    supported_cryptos = ['btc']


class ChainRadar(Service):
    api_homepage = "http://chainradar.com/api"
    service_id = 41
    name = "ChainRadar.com"
    supported_cryptos = ['aeon', 'bbr', 'bcn', 'btc', 'dsh', 'fcn', 'mcn', 'qcn', 'duck', 'mro', 'rd']

    def get_block(self, crypto, block_number='', block_hash='', latest=False):
        if latest:
            url = "http://chainradar.com/api/v1/%s/status" % crypto
            block_number = self.get_url(url).json()['height']

        url = "http://chainradar.com/api/v1/%s/blocks/%s/full" % (crypto, block_number or block_hash)
        r = self.get_url(url).json()
        h = r['blockHeader']

        return dict(
            block_number=h['height'],
            time=arrow.get(h['timestamp']).datetime,
            size=h['blockSize'],
            hash=h['hash'],
            previous_hash=h['prevBlockHash'],
            txids=[x['hash'] for x in r['transactions']],
            tx_count=len(r['transactions'])
        )

class Mintr(Service):
    service_id = 42
    name = "Mintr.org"
    domain = "http://{coin}.mintr.org"
    supported_cryptos = ['ppc', 'emc']
    api_homepage = "https://www.peercointalk.org/index.php?topic=3998.0"
    explorer_tx_url = "https://{coin}.mintr.org/tx/{txid}"
    explorer_address_url = "https://{coin}.mintr.org/address/{address}"
    explorer_blocknum_url = "https://{coin}.mintr.org/block/{blocknum}"
    explorer_blockhash_url = "https://{coin}.mintr.org/block/{blockhash}"

    @classmethod
    def _get_coin(cls, crypto):
        if crypto == 'ppc':
            return 'peercoin'
        if crypto == 'emc':
            return 'emercoin'

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/api/address/balance/%s" % (
            self.domain.format(coin=self._get_coin(crypto)), address
        )
        r = self.get_url(url).json()

        if 'error' in r:
            raise Exception("Mintr returned error: %s" % r['error'])

        return float(r['balance'])

    def get_transactions(self, crypto, address):
        url = "%s/api/address/balance/%s/full" % (
            self.domain.format(coin=self._get_coin(crypto)), address
        )
        txs = []
        for tx in self.get_url(url).json()['transactions']:
            if not tx['sent'] and not tx['received']:
                continue

            amount = float(tx['sent'] or tx['received'])
            txs.append(dict(
                address=address,
                amount=amount if tx['received'] else -1 * amount,
                date=arrow.get(tx['time']).datetime,
                txid=tx['tx_hash'],
            ))
        return txs

    def get_single_transaction(self, crypto, txid):
        url = "%s/api/tx/hash/%s" % (
            self.domain.format(coin=self._get_coin(crypto)), txid
        )

        d = self.get_url(url).json()
        return dict(
            time=arrow.get(d['time']).datetime,
            total_in=float(d['valuein']),
            total_out=float(d['valueout']),
            fee=float(d['fee']),
            inputs=[{'address': x['address'], 'value': x['value']} for x in d['vin']],
            outputs=[{'address': x['address'], 'value': x['value']} for x in d['vout']],
            txid=txid,
        )

    def get_block(self, crypto, block_number='', block_hash='', latest=False):
        by = "latest"
        if block_number:
            by = "height/" + block_number
        elif block_hash:
            by = "hash/" + block_hash

        url = "%s/api/block/%s" % (
            self.domain.format(coin=self._get_coin(crypto)), by
        )

        b = self.get_url(url).json()

        return dict(
            block_number=int(b['height']),
            time=arrow.get(b['time']).datetime,
            hash=b['blockhash'],
            previous_hash=b['previousblockhash'],
            txids=[x['tx_hash'] for x in b['transactions']],
            tx_count=int(b['numtx']),
            size=int(b['size']),
            sent_value=float(b['valueout']) + float(b['mint']),
            mining_difficulty=float(b['difficulty']),
            merkle_root=b['merkleroot'],
            total_fees=float(b['fee'])
        )


class BlockExplorersNet(Service):
    service_id = 43
    domain = "http://{coin}.blockexplorers.net"
    supported_cryptos = ['gsm', 'erc', 'tx']
    name = "BlockExplorers.Net"

    explorer_tx_url = "https://{coin}.blockexplorers.net/tx/{txid}"
    explorer_address_url = "https://{coin}.blockexplorers.net/address/{address}"
    #explorer_blocknum_url = "https://{coin}.blockexplorers.net/block/{blocknum}"
    explorer_blockhash_url = "https://{coin}.blockexplorers.net/block/{blockhash}"

    @classmethod
    def _get_coin(cls, crypto):
        if crypto == 'gsm':
            return "gsmcoin"
        if crypto == 'erc':
            return 'europecoin'
        if crypto == 'tx':
            return 'transfercoin'


    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/ext/getbalance/%s" % (
            self.domain.format(coin=self._get_coin(crypto)), address
        )
        return float(self.get_url(url).content)

    def get_transactions(self, crypto, address):
        domain = self.domain.format(coin=self._get_coin(crypto))
        url = "%s/ext/getaddress/%s" % (domain, address)
        return self.get_url(url).json()

    def get_single_transaction(self, crypto, txid):
        domain = self.domain.format(coin=self._get_coin(crypto))
        url = "%s/api/getrawtransaction?txid=%s&decrypt=1" % (domain, txid)

        d = self.get_url(url).json()

        if not d['vin'] or not d['vin'][0].get('coinbase'):
            ins = [{'txid': x['txid']} for x in d['vin']]
        else:
            ins = [{'txid': x['coinbase']} for x in d['vin']]

        outs = [{'address': x['scriptPubKey']['addresses'][0], 'value': x['value']} for x in d['vout']]

        return dict(
            time=arrow.get(d['time']).datetime,
            block_hash=d['blockhash'],
            hex=d['hex'],
            inputs=ins,
            outputs=outs,
            txid=txid,
            total_out=sum(x['value'] for x in outs),
            confirmations=d['confirmations'],
        )

    def get_block(self, crypto, block_number='', block_hash='', latest=False):
        domain = self.domain.format(coin=self._get_coin(crypto))

        if latest:
            url = "%s/api/getblockcount" % domain
            block_number = int(self.get_url(url).content)

        if block_number:
            url = "%s/api/getblockhash?index=%s" % (domain, block_number)
            block_hash = self.get_url(url).content

        url = "%s/api/getblock?hash=%s" % (domain, block_hash)
        r = self.get_url(url).json()

        return dict(
            confirmations=r['confirmations'],
            size=r['size'],
            txs=r['tx'],
            tx_count=len(r['txs']),
            time=arrow.get(r['time']).datetime,
            hash=r['hash'],
            block_number=r['height'],
            merkle_root=r['merkleroot'],
            difficulty=r['difficulty'],
        )

class UNOCryptap(BitpayInsight):
    service_id = 44
    supported_cryptos = ['uno']
    protocol = 'http'
    domain = "insight-uno.cryptap.us"
    name = "UNO cryptap"

class RICCryptap(BitpayInsight):
    service_id = 45
    supported_cryptos = ['ric']
    protocol = 'http'
    domain = "insight-ric.cryptap.us"
    name = "RIC cryptap"


class ProHashing(Service):
    service_id = 46
    domain = "prohashing.com"
    name= "ProHashing"

    def get_address_balance(self, crypto, address, confirmations=1):
        url = "https://%s/explorerJson/getAddress?address=%s&coin_id=%s" % (
            self.domain, address, self._get_coin(crypto)
        )
        r = self.get_url(url).json()

        if r.get('message', None):
            raise SkipThisService("Could not get Coin Info: %s" % r['message'])

        return r['balance']

    def get_transactions(self, crypto, address, confirmations=1):
        params = '$params={"page":1,"count":20,"filter":{},"sorting":{"blocktime":"asc"},"group":{},"groupBy":null}'
        url = "https://%s/explorerJson/getTransactionsByAddress?%s&address=%s&coin_id=%s" % (
            self.domain, params, address, self._get_coin(crypto)
        )
        txs = []
        for tx in self.get_url(url).json()['data']:
            txs.append(dict(
                amount=tx['value'],
                date=arrow.get(tx['blocktime']).datetime,
                txid=tx['transaction_hash'],
            ))
        return txs

    def get_single_transaction(self, crypto, txid):
        url = "https://%s/explorerJson/getTransaction?coin_id=%s&transaction_id=%s" % (
            self.domain, self._get_coin(crypto), txid
        )
        tx = self.get_url(url).json()

        return dict(
            time=arrow.get(tx['blocktime'] / 1000).datetime,
            block_hash=tx['block_hash'],
            block_number=tx['block_height'],
            inputs=[dict(address=x['address'], amount=-x['value']) for x in tx['address_inputs']],
            outputs=[dict(address=x['address'], amount=x['value']) for x in tx['address_outputs']],
            txid=txid,
            total_in=tx['total_outputs'],
            total_out=tx['total_outputs'],
            confirmations=tx['confirmations'],
        )

    def _get_coin(self, crypto):
        from crypto_data import crypto_data
        full_name = crypto_data[crypto]['name']
        url = "https://%s/explorerJson/getInfo?coin_name=%s" % (
            self.domain, full_name
        )
        r = self.get_url(url).json()

        if r.get('message', None):
            raise SkipThisService("Could not get Coin Info: %s" % r['message'])

        return r['id']

    def get_block(self, crypto, block_number='', block_hash='', latest=False):
        if latest or block_number:
            raise SkipThisService("Block height and latest not implemented.")

        url = "https://%s/explorerJson/getBlock?coin_id=%s&"% (
            self.domain, self._get_coin(crypto),
        )
        if block_hash:
            url = "%shash=%s" % (
                url, block_hash
            )

        r = self.get_url(url).json()
        return dict(
            confirmations=r['confirmations'],
            size=r['size'],
            txs=[x['hash'] for x in r['tx']],
            tx_count=len(r['tx']),
            time=arrow.get(r['time'] / 1000).datetime,
            hash=r['hash'],
            block_number=r['height'],
            difficulty=r['difficulty'],
        )

class SiampmDashInsight(BitpayInsight):
    service_id = 47
    supported_cryptos = ['dash']
    protocol = "http"
    domain = "insight.dash.siampm.com"
    name = "Siampm Dash Insight"
