import json

from requests.auth import HTTPBasicAuth
from moneywagon.core import (
    Service, NoService, NoData, ServiceError, SkipThisService, currency_to_protocol,
    decompile_scriptPubKey
)
from bitcoin import deserialize
import arrow

from bs4 import BeautifulSoup
import re

import hmac, hashlib, time, requests, base64
from requests.auth import AuthBase

try:
    from urllib import urlencode, quote_plus
except ImportError:
    from urllib.parse import urlencode, quote_plus

def make_standard_nonce():
    return str(int(time.time() * 1000))

class FullNodeCLIInterface(Service):
    service_id = None
    cli_path = "" # set to full path to bitcoin-cli executable

    def get_address_balance(self, crypto, address):
        return self.make_rpc_call(['getbalance', address])

    def get_unspent_outputs(self, crypto, address):
        outs = self.make_rpc_call(['gettxout', address])
        return outs

    def push_tx(self, crypto, tx_hex):
        return self.make_rpc_call(["sendrawtransaction", tx_hex], skip_json=True).strip()

    def get_block(self, crypto, block_hash=None, block_number=None, latest=False):
        if latest:
            block_number = self.make_rpc_call(["getblockcount"])

        if not block_hash:
            block_hash = self.make_rpc_call(["getblockhash", block_number], skip_json=True)

        r = self.make_rpc_call(['getblock', block_hash])
        return dict(
            block_number=r['height'],
            confirmations=r['confirmations'],
            time=arrow.get(r['time']).datetime,
            mining_difficulty=r['difficulty'],
            hash=r['hash'],
            next_hash=r.get('nextblockhash', None),
            size=r['size'],
            merkle_root=r['merkleroot'],
            previous_hash=r['previousblockhash'],
            txids=r['tx'],
            version=r['version']
        )


    def get_single_transaction(self, crypto, txid, skip_input_info=False):
        tx = self.make_rpc_call(
            ["getrawtransaction",  txid,  "1"], internal=skip_input_info
        )

        ins = []
        for n in tx['vin']:
            vout = n['vout']
            address = None
            amount = None
            if not skip_input_info:
                # do recursion to get amount and address of vin
                # "skip_input_info" to avoid infitite recursion
                inner_tx = self.get_single_transaction(crypto, n['txid'], skip_input_info=True)
                the_out = inner_tx['outputs'][vout]
                address = the_out['address']
                amount = the_out['amount']

            ins.append({
                'address': address,
                'amount': amount,
                'txid': n['txid'],
            })

        outs = [
            {
                'address': x['scriptPubKey']['addresses'][0],
                'amount': x['valueSat'],
                'scriptPubKey': x['scriptPubKey']['hex'],
            } for x in tx['vout']
        ]

        return dict(
            txid=tx['txid'],
            confirmations=tx['confirmations'],
            size=tx['size'],
            time=arrow.get(tx['blocktime']).datetime,
            block_hash=tx.get('blockhash', None),
            block_number=tx['height'],
            inputs=ins,
            outputs=outs,
        )


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
        ins = [
            {
                'address': x['addresses'][0],
                'amount': x['output_value'],
                'txid': x['prev_hash'],
            } for x in tx['inputs']
        ]
        outs = [
            {
                'address': x['addresses'][0],
                'amount': x['value'],
                'scriptPubKey': x['script'],
            } for x in tx['outputs']
        ]

        return dict(
            txid=txid,
            confirmations=tx['confirmations'],
            size=tx['size'],
            time=arrow.get(tx['received']).datetime,
            block_hash=tx.get('block_hash', None),
            block_number=tx['block_height'],
            inputs=ins,
            outputs=outs,
            total_in=sum(x['amount'] for x in ins),
            total_out=sum(x['amount'] for x in ins),
            fee=tx['fees'],
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

    def check_error(self, response):
        if 'error' in response.json():
            raise ServiceError("BlockSeer returned error: %s" % response.json()['error'])

        super(BlockSeer, self).check_error(response)

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

    def get_single_transaction(self, crypto, txid):
        url = "%s/tx/%s" % (self.base_url, txid)
        r = self.get_url(url).json()['transaction']

        ins = [
            {
                'address': x['addresses'][0],
                'amount': x['value_int'],
                'txid': x['txid']
            } for x in r['inputs']
        ]
        outs = [
            {
                'address': x['addresses'][0],
                'amount': x['value_int'],
                'scriptPubKey': x['script_pub_key']['hex']
            } for x in r['outputs']
        ]

        return dict(
            time=arrow.get(r['time']).datetime,
            size=r['size'],
            block_number=r['block'],
            inputs=ins,
            outputs=outs,
            txid=txid,
            confirmations=r['confirmations'],
            fee=r['fee_int']
        )


class Cryptonator(Service):
    service_id = 8
    api_homepage = "https://www.cryptonator.com/api"
    name = "Cryptonator"

    def check_error(self, response):
        error = response.json().get('error')
        if error:
            raise ServiceError("Cryptonator returned error: %s" % error)

        super(Cryptonator, self).check_error(response)

    def get_current_price(self, crypto, fiat):
        if crypto == 'xmy':
            crypto = 'myr'
        pair = "%s-%s" % (crypto, fiat)
        url = "https://api.cryptonator.com/api/ticker/%s?utm_referrer=" % pair
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

    def get_block(self, crypto, block_number=None, block_hash=None, latest=False):
        if latest:
            raise SkipThisService("This service can't get block by latest")
        else:
            url = "%s/block/%s/%s" % (
                self.base_url, crypto, block_hash if block_number is None else block_number
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

    def get_single_transaction(self, crypto, txid):
        url = "%s/get_tx/%s/%s" % (self.base_url, crypto, txid)
        r = self.get_url(url).json()['data']
        tx = deserialize(str(r['tx_hex']))

        outs = [
            {
                'address': x['address'],
                'amount': currency_to_protocol(x['value']),
                'scriptPubKey': [
                    p['script'] for p in tx['outs'] if currency_to_protocol(x['value']) == p['value']
                ][0],
            } for x in r['outputs']
        ]
        ins = [
            {
                'address': x['address'],
                'amount': currency_to_protocol(x['value']),
                'txid': x['from_output']['txid'] if x['from_output'] else None,
                'scriptSig': x['script'],
                'n': x['input_no']
            } for x in r['inputs']
        ]

        return dict(
            time=arrow.get(r['time']).datetime,
            block_hash=r['blockhash'],
            hex=r['tx_hex'],
            size=r['size'],
            inputs=ins,
            outputs=outs,
            txid=txid,
            confirmations=r['confirmations'],
            locktime=r['locktime'],
            version=r['version']
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

    def get_single_transaction(self, crypto, txid):
        url = "%s/transactions/%s" % (self.base_url, txid)
        r = self.get_url(url).json()
        ins = [
            {
                'address': x['addresses'][0] if x['addresses'] else None,
                'txid': x['output_hash'],
                'amount': x['value']
            } for x in r['inputs']
        ]

        outs = [
            {
                'address': x['addresses'][0] if x['addresses'] else None,
                'scriptPubKey': x['script'],
                'amount': x['value']
            } for x in r['outputs']
        ]

        return dict(
            time=arrow.get(r['block_time']).datetime,
            confirmations=r.get('confirmations', 0),
            fee=r['fees'],
            inputs=ins,
            outputs=outs,
            txid=txid,
            block_number=r['block_height'],
            block_hash=r['block_hash']
        )


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

    def check_error(self, response):
        if response.status_code == 404:
            msg = "; ".join(response.json()['messages'])
            raise ServiceError("BitEasy returned 404: %s" % msg)

        super(BitEasy, self).check_error(response)

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
        latest_block_number = self.get_block('btc', latest=True)['block_number']

        url = "https://%s/tx-index/%s?format=json" % (
            self.domain, txid
        )
        tx = self.get_url(url).json()
        outs = [
            {
                'address': x['addr'],
                'amount': x['value'],
                'scriptPubKey': x['script']
            } for x in tx['out']
        ]
        ins = []

        for in_ in tx['inputs']:
            if 'prev_out' in in_:
                prev = in_['prev_out']
                ins.append(
                    {'address': prev['addr'], 'amount': prev['value']}
                )

        block_number = tx.get('block_height', None)

        return dict(
            txid=txid,
            block_number=block_number,
            size=tx['size'],
            time=arrow.get(tx['time']).datetime,
            confirmations=(latest_block_number - block_number) if block_number else 0,
            inputs=ins,
            outputs=outs,
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

    def get_block(self, crypto, block_number=None, block_hash=None, latest=False):
        if block_hash:
            raise SkipThisService("There is no way to get block by hash")

        url = "https://%s/latestblock" % self.domain
        latest_block_number = self.get_url(url).json()['height']

        if latest:
            block_number = latest_block_number

        url = "https://%s/block-height/%s?format=json" % (self.domain, block_number)
        r = self.get_url(url).json()['blocks'][0]
        confirmations = latest_block_number - r['height']
        return dict(
            block_number=r['height'],
            version=r['ver'],
            confirmations=confirmations,
            time=arrow.get(r['time']).datetime,
            size=r['size'],
            hash=r['hash'],
            merkle_root=r['mrkl_root'],
            previous_hash=r.get('prev_block', None),
            txids=[x['hash'] for x in r['tx']],
            tx_count=r['n_tx']
        )




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
            inputs=[
                {
                    'address': x['address'],
                    'amount': float(x['value']),
                    'txid': x['previous_output']['hash']
                } for x in r['inputs']
            ],
            outputs=[
                {
                    'address': x['address'],
                    'amount': float(x['value'])
                } for x in r['outputs']
            ],
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

    def check_error(self, response):
        if response.status_code == 499:
            raise ServiceError("CryptoID returned error: %s" % response.content)

        super(CryptoID, self).check_error(response)

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
            inputs=[
                {
                    'address': x['addr'],
                    'amount': int(x['amount'] * 1e8),
                    'txid': x['received_from']['tx']
                } for x in r['inputs']
            ],
            outputs=[
                {
                    'address': x['addr'],
                    'amount': int(x['amount'] * 1e8),
                    'scriptPubKey': x['script'],
                } for x in r['outputs']
            ],
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
        'nmc', 'wds', 'ber', 'scn', 'sc0', 'wdc', 'nvc', 'cas', 'xmy'
    ]

    def get_balance(self, crypto, address, confirmations=1):
        url = "http://cryptap.us/%s/explorer/q/addressbalance/%s" % (crypto, address)
        return float(self.get_url(url).content)


class BitpayInsight(Service):
    service_id = 28
    supported_cryptos = ['btc']
    domain = "insight.bitpay.com"
    protocol = 'https'
    api_homepage = "{protocol}://{domain}/api"
    explorer_address_url = "{protocol}://{domain}/address/{address}"
    explorer_tx_url = "{protocol}://{domain}/tx/{txid}"
    api_tag = 'api'
    name = "Bitpay Insight"
    socketio_url = "%s://%s" % (protocol, domain)
    version = 5

    def check_error(self, response):
        if response.status_code == 400:
            raise ServiceError(response.content)

        super(BitpayInsight, self).check_error(response)

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s://%s/%s/addr/%s/balance" % (self.protocol, self.domain, self.api_tag, address)
        return float(self.get_url(url).content) / (1e8 if self.version < 5 else 1)

    def _format_tx(self, tx, addresses):
        matched_addresses = []
        my_outs = 0
        my_ins = 0
        for address in addresses:
            for x in tx['vout']:
                if address in x['scriptPubKey'].get('addresses', []):
                    my_outs += float(x['value'])
                    matched_addresses.append(address)
            for x in tx['vin']:
                if address in x['addr']:
                    my_ins += float(x['value'])
                    matched_addresses.append(address)

        return dict(
            amount=my_outs - my_ins,
            date=arrow.get(tx['time']).datetime if tx.get('time', False) else None,
            txid=tx['txid'],
            confirmations=tx.get('confirmations', 0),
            addresses=list(set(matched_addresses))
        )

    def get_transactions(self, crypto, address):
        url = "%s://%s/%s/txs/?address=%s" % (self.protocol, self.domain, self.api_tag, address)
        response = self.get_url(url)
        transactions = []
        for tx in response.json()['txs']:
            transactions.append(self._format_tx(tx, [address]))
        return transactions

    def get_transactions_multi(self, crypto, addresses):
        url = "%s://%s/%s/addrs/%s/txs" % (
            self.protocol, self.domain, self.api_tag, ','.join(addresses)
        )
        r = self.get_url(url).json()
        txs = []
        for tx in r['items']:
            txs.append(self._format_tx(tx, addresses))
        return txs

    def _extract_scriptPubKey(self, scriptPubKey):
        #import debug
        if 'hex' in scriptPubKey:
            return scriptPubKey['hex']

        # old version of insight, we have to build the hex encoding
        # ourselves.
        return decompile_scriptPubKey(scriptPubKey['asm'])

    def get_single_transaction(self, crypto, txid):
        url = "%s://%s/%s/tx/%s" % (self.protocol, self.domain, self.api_tag, txid)
        d = self.get_url(url).json()

        block_time = None
        if d.get('blocktime'):
            block_time = arrow.get(d['blocktime']).datetime

        return dict(
            time=block_time,
            block_number=d.get("blockheight"),
            size=d['size'],
            confirmations=d['confirmations'] if block_time else 0,
            fee=currency_to_protocol(d['fees']) if 'fees' in d else None,
            inputs=[
                {
                    'address': x['addr'],
                    'amount': currency_to_protocol(x['value']),
                    'txid': x['txid'],
                    'n': x['n'],
                    'scriptSig': x['scriptSig'].get('hex'),
                    'sequence': x['sequence']
                } for x in d['vin'] if 'addr' in x
            ] + [
                {'coinbase': x['coinbase']} for x in d['vin'] if 'coinbase' in x
            ],
            outputs=[
                {
                    'address': x['scriptPubKey'].get('addresses', [None])[0],
                    'amount': currency_to_protocol(x['value']),
                    'scriptPubKey': self._extract_scriptPubKey(x['scriptPubKey'])
                } for x in d['vout']
            ],
            txid=txid,
            version=d['version'],
            locktime=d['locktime'],
        )

    def _format_utxo(self, utxo):
        return dict(
            txid=utxo['txid'],
            vout=utxo['vout'],
            scriptPubKey=utxo.get('scriptPubKey'),
            output="%s:%s" % (utxo['txid'], utxo['vout']),
            amount=currency_to_protocol(utxo['amount']),
            confirmations=utxo.get('confirmations', None),
            address=utxo['address']
        )

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        url = "%s://%s/%s/addr/%s/utxo?noCache=1" % (self.protocol, self.domain, self.api_tag, address)
        utxos = []
        for utxo in self.get_url(url).json():
            utxos.append(self._format_utxo(utxo))
        return utxos

    def get_unspent_outputs_multi(self, crypto, addresses, confirmations=1):
        url = "%s://%s/%s/addrs/%s/utxo?noCache=1" % (self.protocol, self.domain, self.api_tag, ','.join(addresses))
        utxos = []
        for utxo in self.get_url(url).json():
            utxos.append(self._format_utxo(utxo))
        return utxos

    def get_block(self, crypto, block_number=None, block_hash=None, latest=False):
        if latest:
            url = "%s://%s/%s/status?q=getLastBlockHash" % (self.protocol, self.domain, self.api_tag)
            block_hash = self.get_url(url).json()['lastblockhash']

        elif block_number is not None:
            url = "%s://%s/%s/block-index/%s" % (self.protocol, self.domain, self.api_tag, block_number)
            block_hash = self.get_url(url).json()['blockHash']

        url = "%s://%s/%s/block/%s" % (self.protocol, self.domain, self.api_tag, block_hash)

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
        url = "%s://%s/%s/tx/send" % (self.protocol, self.domain, self.api_tag)
        return self.post_url(url, {'rawtx': tx_hex}).json()['txid']


    def get_optimal_fee(self, crypto, tx_bytes):
        url = "%s://%s/%s/utils/estimatefee?nbBlocks=2" % (self.protocol, self.domain, self.api_tag)
        return self.get_url(url).json()

class MYRCryptap(BitpayInsight):
    service_id = 30
    protocol = 'http'
    supported_cryptos = ['xmy']
    domain = "insight-myr.cryptap.us"
    name = "MYR cryptap"
    version = 0.2


class BirdOnWheels(BitpayInsight):
    service_id = 31
    supported_cryptos = ['xmy']
    domain = "birdonwheels5.no-ip.org:3000"
    name = "Bird on Wheels"
    version = 0.2


class Verters(BitpayInsight):
    service_id = 32
    supported_cryptos = ['vtc']
    domain = "explorer.verters.com"
    name = "Verters"
    ssl_verify = False
    version = 0.2

class ReddcoinCom(BitpayInsight):
    service_id = 33
    supported_cryptos = ['rdd']
    domain = "live.reddcoin.com"
    name = "Reddcoin.com"
    version = 0.2

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

    def get_single_transaction(self, crypto, txid):
        url = "%s/api/v1/tx/%s" % (self.base_url, txid)
        r = self.get_url(url).json()
        tx = deserialize(str(r['hex']))

        outs = [
            {
                'address': x['account'],
                'amount': x['value'],
                'scriptPubKey': [p['script'] for p in tx['outs'] if x['value'] == p['value']][0],
            } for x in r['entries'] if x['value'] > 0
        ]

        def get_inputs(ins, entries):
            ins.sort(key=lambda x: x['previousOutputIndex'])
            inputs = []
            inputs_index = 0
            for entry in entries:
                if entry['value'] < 0:
                    inputs.append({
                        'address': entry['account'],
                        'amount': abs(entry['value']),
                        'txid': ins[inputs_index]['previousHash']
                    })
                    inputs_index += 1
            return inputs

        ins = get_inputs(r['inputs'], r['entries'])

        return dict(
            time=arrow.get(r['date']).datetime,
            size=len(r['hex']) / 2,
            confirmations=r.get('confirmations', 0),
            fee=r['fee'],
            inputs=ins,
            outputs=outs,
            txid=txid,
            hex=r['hex'],
            block_number=r['height'],
            block_hash=r['blockhash']
        )

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
        for tx in response['history'] + response.get('pending', []):
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
            confirmations=1 if d['status'] == 'Confirmed' else 0,
            time=arrow.get(d['time']).datetime,
            inputs=[{'address': x['address'], 'amount': x['value']} for x in d['vin']],
            outputs=[{'address': x['address'], 'amount': x['value']} for x in d['vout']],
            txid=txid,
            fees=d['fee'],
            size=d['size']
        )


class BlockExplorerCom(BitpayInsight):
    service_id = 38
    supported_cryptos = ['btc']
    domain = "blockexplorer.com"
    name = "BlockExplorer.com"
    version = 0.4

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
    ssl_verify = False # ssl is broken (set to true when it's fixed)

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
            inputs=[{'address': x['address'], 'amount': x['value']} for x in d['vin']],
            outputs=[{'address': x['address'], 'amount': x['value']} for x in d['vout']],
            txid=txid,
        )

    def get_block(self, crypto, block_number=None, block_hash=None, latest=False):
        by = "latest"
        if block_number is not None:
            by = "height/%s" % block_number
        elif block_hash is not None:
            by = "hash/%s" % block_hash

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

class Iquidus(Service):
    @classmethod
    def _get_coin(cls, crypto):
        return ""

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/ext/getbalance/%s" % (
            self.base_url.format(coin=self._get_coin(crypto)), address
        )
        response = self.get_url(url).json()

        if type(response) == dict and response.get('error') == 'address not found.':
            return 0

        return response

    def get_transactions(self, crypto, address):
        domain = self.base_url.format(coin=self._get_coin(crypto))
        url = "%s/ext/getaddress/%s" % (domain, address)
        r = self.get_url(url).json()
        if 'error' in r and r['error'] == 'address not found.':
            return []

    def get_single_transaction(self, crypto, txid):
        domain = self.base_url.format(coin=self._get_coin(crypto))
        url = "%s/api/getrawtransaction?txid=%s&decrypt=1" % (domain, txid)

        d = self.get_url(url).json()

        if not d['vin'] or not d['vin'][0].get('coinbase'):
            ins = [{'txid': x['txid']} for x in d['vin']]
        else:
            ins = [{'txid': x['coinbase']} for x in d['vin']]

        outs = [{
            'address': x['scriptPubKey']['addresses'][0],
            'amount': int(x['value'] * 1e8),
            'scriptPubKey': x['scriptPubKey']['hex']
        } for x in d['vout']]

        return dict(
            time=arrow.get(d['time']).datetime,
            block_hash=d['blockhash'],
            hex=d['hex'],
            inputs=ins,
            outputs=outs,
            txid=txid,
            total_out=sum(x['amount'] for x in outs),
            confirmations=d['confirmations'],
        )

    def get_block(self, crypto, block_number=None, block_hash=None, latest=False):
        domain = self.base_url.format(coin=self._get_coin(crypto))

        if latest:
            block_number = self.small_data(crypto, latest_height=True)

        if block_number is not None:
            block_hash = self.small_data(crypto, hash_for_height=block_number)

        url = "%s/api/getblock?hash=%s" % (domain, block_hash)
        r = self.get_url(url).json()

        return dict(
            confirmations=r.get('confirmations'),
            size=r['size'],
            txs=r['tx'],
            tx_count=len(r['tx']),
            time=arrow.get(r['time']).datetime,
            hash=r['hash'],
            block_number=r['height'],
            merkle_root=r['merkleroot'],
            difficulty=r['difficulty'],
        )

    def small_data(self, crypto, **kwargs):
        domain = self.base_url.format(coin=self._get_coin(crypto))

        if 'latest_height' in kwargs:
            url = "%s/api/getblockcount" % domain
            return int(self.get_url(url).content)

        if 'hash_for_height' in kwargs:
            block_number = kwargs['hash_for_height']
            url = "%s/api/getblockhash?index=%s" % (domain, block_number)
            return self.get_url(url).content


class HolyTransaction(Iquidus):
    service_id = 43
    base_url = "http://{coin}.holytransaction.com"
    name = "Holy Transactions"

    explorer_tx_url = "https://{coin}.holytransaction.com/tx/{txid}"
    explorer_address_url = "https://{coin}.holytransaction.com/address/{address}"
    #explorer_blocknum_url = "https://{coin}.blockexplorers.net/block/{blocknum}"
    explorer_blockhash_url = "https://{coin}.holytransaction.com/block/{blockhash}"
    api_homepage = "https://dash.holytransaction.com/info"

    @classmethod
    def _get_coin(cls, crypto):
        if crypto == 'gsm':
            return "gsmcoin"
        if crypto == 'erc':
            return 'europecoin'
        if crypto == 'tx':
            return 'transfercoin'
        if crypto == 'dash':
            return 'dash'
        if crypto == 'ltc':
            return 'litecoin'
        if crypto == 'bc':
            return 'blackcoin'
        if crypto == 'ppc':
            return 'peercoin'
        if crypto == 'doge':
            return 'dogecoin'
        if crypto == 'grc':
            return 'gridcoin'
        if crypto == 'blk':
            return 'blackcoin'


class UNOCryptap(BitpayInsight):
    service_id = 44
    supported_cryptos = ['uno']
    protocol = 'http'
    domain = "insight-uno.cryptap.us"
    name = "UNO cryptap"
    version = 0.0


class RICCryptap(BitpayInsight):
    service_id = 45
    supported_cryptos = ['ric']
    protocol = 'http'
    domain = "insight-ric.cryptap.us"
    name = "RIC cryptap"
    version = 0.0


class ProHashing(Service):
    service_id = 46
    domain = "prohashing.com"
    name= "ProHashing"

    def get_balance(self, crypto, address, confirmations=1):
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
        from moneywagon.crypto_data import crypto_data
        full_name = crypto_data[crypto]['name']
        url = "https://%s/explorerJson/getInfo?coin_name=%s" % (
            self.domain, full_name
        )
        r = self.get_url(url).json()

        if r.get('message', None):
            raise SkipThisService("Could not get Coin Info: %s" % r['message'])

        return r['id']

    def get_block(self, crypto, block_number=None, block_hash=None, latest=False):
        if latest or block_number is not None:
            raise SkipThisService("Block height and latest not implemented.")

        url = "https://%s/explorerJson/getBlock?coin_id=%s&" % (
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
    version = 0.2

class BlockExperts(Service):
    service_id = 48
    name = "Block Experts"
    base = "https://www.blockexperts.com"

    def _get_coin(self, crypto):
        if crypto == 'hemp':
            return 33
        if crypto == 'dime':
            return 57
        if crypto == 'dope':
            return 19

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/api?coin=%s&action=getbalance&address=%s" % (
            self.base, crypto, address
        )
        return float(self.get_url(url).content)

    def get_single_transaction(self, crypto, txid):
        url = "%s/include/ajax/ajax.tx.raw.php?coin_id=%s&tx=%s" % (
            self.base, self._get_coin(crypto), txid
        )
        resp = self.get_url(url).json()
        return dict(
            time=arrow.get(tx['blocktime']).datetime,
            block_hash=tx['blockhash'],
            inputs=[dict(address=x['address'], amount=-x['value']) for x in tx['vin']],
            outputs=[dict(address=x['scriptPubKey']['address'], amount=x['value']) for x in tx['vout']],
            txid=txid,
            version=tx['version'],
            confirmations=tx['confirmations'],
        )

    def get_block(self, crypto, block_number=None, block_hash=None, latest=False):
        if latest:
            raise SkipThisService("Cant get by latest")
            url = "https://www.blockexperts.com/api?coin=hemp&action=getheight"
            block_height = int(self.get_url(url).content)

        if block_number is not None:
            raise SkipThisService("Cant get by block number")

        url = "%s/include/ajax/ajax.block.raw.php?coin_id=%s&block_hash=%s" % (
            self.base, self._get_coin(crypto), block_hash
        )
        r = self.get_url(url).json()
        return dict(
            confirmations=r['confirmations'],
            size=r['size'],
            txs=r['tx'],
            tx_count=len(r['tx']),
            time=arrow.get(r['time']).datetime,
            hash=r['hash'],
            block_number=r['height'],
            difficulty=r['difficulty'],
            merkle_root=r['merkleroot'],
        )

class MultiCoins(Service):
    service_id = 49
    supported_cryptos = ['ppc']

    def push_tx(self, crypto, tx_hex):
        """
        This method is untested.
        """
        url = "https://multicoins.org/api/v1/tx/push/ppc"
        return self.post_url(url, {'hex': tx_hex})

class BitcoinChain(Service):
    service_id = 50
    base = "https://api-r.bitcoinchain.com"
    supported_cryptos = ['btc']

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/v1/address/%s" % (self.base, address)
        return self.get_url(url).json()[0]['balance']

    def get_balance_multi(self, crypto, addresses, confirmations=1):
        url = "%s/v1/address/%s" % (self.base, ','.join(addresses))
        ret = {}
        for address_data in self.get_url(url).json():
            address = address_data['address']
            ret[address] = address_data['balance']

        return ret

    def get_transactions(self, crypto, address, confirmations=1):
        url = "%s/v1/address/txs/%s" % (self.base, address)
        response = self.get_url(url).json()[0]
        txs = []
        for tx in response:
            txs.append(dict(
                txid=tx['tx']['self_hash'],
                date=arrow.get(tx['tx']['block_time']).datetime,
            ))
        return txs

    def get_single_transaction(self, crypto, txid):
        url = "%s/v1/tx/%s" % (self.base, txid)
        r = self.get_url(url).json()

class CounterParty(Service):
    protocol = "http"
    port = None
    username = None
    password = None

    def check_error(self, response):
        j = response.json()
        if 'error' in j:
            e = j['error']
            raise ServiceError("Error code: %s %s" % (e['code'], e['message']))

        super(CounterParty, self).check_error(response)

    def authed_post_url(self, payload):
        auth = HTTPBasicAuth(self.username, self.password)
        headers = {'content-type': 'application/json'}
        url = "%s://%s:%s/api/" % (self.protocol, self.domain, self.port)
        return self.post_url(url, data=json.dumps(payload), auth=auth, headers=headers).json()

    def get_balance(self, crypto, address, confirmations=1):
        payload = {
            "method": "get_balances",
            "params": {
                "filters": [{"field": "address", "op": "==", "value": address}]
            },
            "jsonrpc": "2.0",
            "id": 0,
        }
        results = self.authed_post_url(payload)['result']
        for r in results:
            if r['address'] == address and r['asset'].lower() == crypto.lower():
                return r['quantity'] / 1e8

    def get_balance_multi(self, crypto, addresses, confirmations=1):
        payload = {
            "method": "get_balances",
            "params": {
                "filters": [{"field": "address", "op": "==", "value": x} for x in addresses],
                "filterop": "or"
            },
            "jsonrpc": "2.0",
            "id": 0,
        }
        results = self.authed_post_url(payload)['result']
        ret = {}
        for r in results:
            ret[r['address']] = r['quantity'] / 1e8

        return ret

    def _format_txs(self, credits, debits):
        txs = []
        for i, results in enumerate([credits, debits]):
            if i == 0:
                sign = 1
            else:
                sign = -1

            for tx in results:
                if tx['asset'].upper() != crypto.upper():
                    continue
                txs.append(dict(
                    amount=tx['quantity'] / 1e8 * sign,
                    txid=tx['event'],
                    address=tx['address'],
                    date=None,
                    counterparty=True
                ))
        return txs

    def get_transactions(self, crypto, address, confirmations=1):
        payload = {
            "method": "get_credits",
            "params": {
                "filters": [
                    {"field": "address", "op": "==", "value": address},
                    {"field": "asset", "op": "==", "value": crypto.upper()},
                ]
            },
            "jsonrpc": "2.0",
            "id": 0,
        }
        credits = self.authed_post_url(payload)['result']

        payload = {
            "method": "get_debits",
            "params": {
                "filters": [
                    {"field": "address", "op": "==", "value": address},
                    {"field": "asset", "op": "==", "value": crypto.upper()},
                ]
            },
            "jsonrpc": "2.0",
            "id": 0,
        }
        debits = self.authed_post_url(payload)['result']
        return self._format_txs(credits, debits)

    def get_transactions_multi(self, crypto, addresses):
        payload = {
            "method": "get_credits",
            "params": {
                "filters": [
                    {"field": "address", "op": "==", "value": address} for address in addresses
                ],
                "filterop": "or"
            },
            "jsonrpc": "2.0",
            "id": 0,
        }
        credits = self.authed_post_url(payload)['result']

        payload = {
            "method": "get_debits",
            "params": {
                "filters": [
                    {"field": "address", "op": "==", "value": address} for address in addresses
                ],
                "filterop": "or"
            },
            "jsonrpc": "2.0",
            "id": 0,
        }
        debits = self.authed_post_url(payload)['result']
        return self._format_txs(credits, debits)

    def get_single_transaction(self, crypto, txid):
        from moneywagon import get_single_transaction
        tx = get_single_transaction('btc', txid)
        return tx

    def make_unsigned_move_tx(self, crypto, amount, from_address, to_address):
        payload = {
            "method": "create_send",
            "params": {
                "source": from_address,
                "destination": to_address,
                "asset": crypto.upper(),
                "quantity": int(amount * 1e8),
                'encoding': "opreturn"
            },
            "jsonrpc": "2.0",
            "id": 0,
        }
        return self.authed_post_url(payload)['result']

    def get_unspent_outputs(self, crypto, address, confirmations=1):
        raise Exception("CounterParty does not use unspent outputs")

    def push_tx(self, crypto, tx_hex):
        from moneywagon import push_tx
        return push_tx('btc', tx_hex, random=True)

class CoinDaddy1(CounterParty):
    service_id = 52
    port = 4000
    domain = "public.coindaddy.io"
    username = 'rpc'
    password = '1234'
    name = "Coin Daddy #1"

class CoinDaddy2(CoinDaddy1):
    service_id = 53
    port = 4100
    name = "Coin Daddy #2"

class CounterPartyChain(Service):
    service_id = 54
    api_homepage = "https://counterpartychain.io/api"

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://counterpartychain.io/api/balances/%s" % address
        response = self.get_url(url).json()
        if response['error']:
            return 0

        for balance in response['data']:
            if balance['asset'].upper() == crypto.upper():
                return float(balance['amount'])

    def push_tx(self, crypto, tx_hex):
        from moneywagon import push_tx
        return push_tx('btc', tx_hex, random=True)

class EtherChain(Service):
    service_id = 55
    name = "EtherChain"
    api_homepage = "https://etherchain.org/documentation/api/"

    def get_current_price(self, crypto, fiat):
        url = "https://etherchain.org/api/basic_stats"
        price = self.get_url(url).json()['data']['price']
        if fiat.lower() in ['btc', 'usd']:
            return price[fiat.lower()]
        return self.convert_currency('usd', price['usd'], fiat)

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://etherchain.org/api/account/%s" % address
        data = self.get_url(url).json()['data']
        return data[0]['balance'] / 1e18

class VTConline(Iquidus):
    service_id = 57
    name = "VTCOnline.org"
    base_url = "https://explorer.vtconline.org"
    supported_cryptos = ['vtc']

class Etherscan(Service):
    service_id = 58
    name = "Etherscan"
    supported_cryptos = ['eth']

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://api.etherscan.io/api?module=account&action=balance&address=%s&tag=latest" % address
        response = self.get_url(url).json()
        return int(response['result']) / 1e18


class FeathercoinCom2(BitcoinAbe):
    service_id = 68
    supported_cryptos = ['ftc']
    base_url = "http://explorer.feathercoin.com/chain/feathercoin"
    name = "Feathercoin.com (Abe)"


class ChainTips(BitpayInsight):
    service_id = 69
    domain = "fsight.chain.tips"
    supported_cryptos = ['ftc']
    name = "Chain Tips (Insight))"
    version = 0.2


class TradeBlock(Service):
    service_id = 71

    def get_single_transaction(self, crypto, txid):
        raise SkipThisService("No scriptPubKey in output")
        url = "https://tradeblock.com/api/blockchain/tx/%s/p" % txid
        tx = self.get_url(url).json()['data']

        ins = [{'txid': x['prev_out']['hash'], 'amount': x['value']} for x in tx['ins']]

        outs = [x for x in tx['outs']]

        return dict(
            txid=txid,
            size=tx['size'],
            time=arrow.get(tx['time_received']).datetime,
            block_hash=tx.get('block_hash', None),
            block_number=tx['block'],
            inputs=ins,
            outputs=outs,
            fees=tx['fee'],
        )

class MasterNodeIO(BitpayInsight):
    service_id = 72
    domain = "blockchain.masternode.io"
    supported_cryptos = ['dash']
    name = "Masternode.io (Insight)"
    version = 0.0


class DashOrgInsight(BitpayInsight):
    service_id = 73
    domain = "insight.dash.org"
    api_tag = "insight-api-dash"
    supported_cryptos = ['dash']
    protocol = "http"
    name = "Dash.org (Insight)"
    version = 0.5


class LocalBitcoinsChain(BitpayInsight):
    service_id = 74
    domain = "localbitcoinschain.com"
    name = "LocalBitcoinsChain (Insight)"
    version = 0.4


class ETCchain(Service):
    service_id = 75
    base_url = "https://etcchain.com/api/v1/"

    def get_balance(self, crypto, address, confirmations=1):
        url = "%sgetAddressBalance?address=%s" % (self.base_url, address)
        r = self.get_url(url)
        if crypto.lower() == 'etc':
            return r.json()['balance']
        if crypto.lower() == 'eth':
            return r.json()['eth_balance']


class Bchain(Service):
    service_id = 76

    def _get_balance(self, crypto, address, confirmations=1):
        url = "https://bchain.info/%s/addr/%s" % (crypto.upper(), address)
        doc = BeautifulSoup(self.get_url(url).content, "html.parser")
        info_script_body = doc.find_all("script")[4].string
        balance = re.findall(";\n\t\tvar balance =.(\d*);", info_script_body)[0]
        return float(balance) / 1e8

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://bchain.info/%s/api/balance/%s" % (crypto, address)
        resp = self.get_url(url)
        return resp.json()['balance'] / 1e8

class PressTab(Service):
    service_id = 79

    def get_balance(self, crypto, address, confirmations=1):
        url = "http://www.presstab.pw/phpexplorer/%s/api.php?address=%s" % (
            crypto.upper(), address
        )
        r = self.get_url(url).json()
        return r['balance']

class MyNXT(Service):
    service_id = 80

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://www.mynxt.info/blockexplorer/nxt/api_getFullAccount.php?account=%s" % address
        r = self.get_url(url).json()
        return float(r['balanceNQT']) / 1e8

class ZChain(Service):
    service_id = 81

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://api.zcha.in/v2/mainnet/accounts/%s" % address
        r = self.get_url(url).json()
        return r['balance']


class BeavercoinBlockchain(BitpayInsight):
    service_id = 83
    domain = "blockchain.beavercoin.org"
    supported_cryptos = ['bvc']
    name = "Beavercoin (insight)"
    protocol = "http"
    version = 0.0


class CryptoChat(Iquidus):
    service_id = 84
    base_url = "http://{coin}.thecryptochat.net"

    @classmethod
    def _get_coin(cls, crypto):
        if crypto == 'bun':
            return "bunnycoin"
        if crypto == 'tse':
            return "tattoocoin"


class LemoncoinOfficial(Iquidus):
    service_id = 85
    base_url = "http://45.32.180.199:3001/"
    supported_crypto = ['lemon']

class GeertcoinExplorer(Iquidus):
    service_id = 86
    base_url = "http://geertcoin.com:1963"
    supported_crypto = ['geert']

class UnlimitedCoinOfficial(Iquidus):
    service_id = 87
    base_url = "http://unlimitedcoin.info:3001"
    supported_cryptos = ['ulm']

class MarscoinOfficial(BitpayInsight):
    service_id = 88
    domain = "explore.marscoin.org"
    supported_cryptos = ['mars']
    protocol = "http"
    name = "MarsCoin.org (Insight)"
    version = 0.2

class TerracoinIO(BitcoinAbe):
    service_id = 97
    base_url = "https://explorer.terracoin.io/chain/Sha256NmcAuxPowChain"
    supported_cryptos = ['trc']

class VergeCurrencyInfo(Iquidus):
    service_id = 98
    base_url = "http://vergecurrency.info"
    supported_cryptos = ['xvg']
    name = "VergeCurrencyInfo"

class FujiInsght(BitpayInsight):
    service_id = 99
    domain = "explorer.fujicoin.org"
    protocol = 'http'
    supported_cryptos = ['fjc']
    version = 0.2

class WebBTC(Service):
    service_id = 100
    supported_cryptos = ['btc', 'nmc']

    def get_balance(self, crypto, address, confirmaions=1):
        coin_name = 'bitcoin'
        if crypto.lower() == 'nmc':
            coin_name = 'namecoin'
        url = "http://%s.webbtc.com/address/%s.json" % (coin_name, address)
        return self.get_url(url).json()['balance'] / 1e8


class PesetacoinInfo(Iquidus):
    service_id = 103
    base_url = "http://explorer.pesetacoin.info"


class VChainInfo(Iquidus):
    service_id = 104
    name = "Chain.info (iquidus)"
    base_url = "https://explorer.vchain.info/"
    supported_cryptos = ['xvc']


class PresetacoinInsight(BitpayInsight):
    service_id = 107
    domain = "live.pesetacoin.info"
    protocol = "http"
    supported_cryptos = ['ptc']
    version = 0.2


class MercerWeiss(BitpayInsight):
    service_id = 108
    domain = "insight.mercerweiss.com"
    supported_cryptos = ['zec']
    protocol = 'http'
    version = 0.4


class NoLimitCoinIquidus(Iquidus):
    service_id = 112
    base_url = "http://nolimitcoin.info"
    supported_cryptos = ['nlc2']


class CloakCoinIquidus(Iquidus):
    service_id = 113
    base_url = 'https://explorer.cloakcoin.com'
    supported_cryptos = ['cloak']


class MergeCoinInsight(BitpayInsight):
    service_id = 114
    domain = "www.mergechain.com:3000"
    supported_cryptos = ['mgc']
    protocol = "http"
    version = 0.2


class ParticlInsight(BitpayInsight):
    service_id = 117
    domain = "explorer.particl.io"
    supported_cryptos = ['part']
    api_tag = "particl-insight-api"
    version = 0.4


class BlockDozer(BitpayInsight):
    service_id = 118
    name = "BlockDozer"
    domain = "blockdozer.com"
    api_tag = "insight-api"
    protocol = "http"
    supported_cryptos = ['bch']
    version = 0.0


class LeoCoinInsight(BitpayInsight):
    service_id = 119
    domain = "insight.leocoin.org"
    supported_cryptos = ['leo']
    version = 0.2


class UnifyIquidus(Iquidus):
    service_id = 121
    base_url = "http://unify-explorer.dnsalias.com"
    supported_cryptos = ['unify']


class Groestlsight(BitpayInsight):
    service_id = 122
    domain = "groestlsight.groestlcoin.org"
    supported_cryptos = ['grs']
    protocol = "http"
    name = "Groestlsight"
    version = 0.2


class DigiExplorer(BitpayInsight):
    service_id = 123
    domain = "digiexplorer.info"
    supported_cryptos = ['dgb']
    name = "DigiExplorer"
    version = 0.2


class BitcoinComCashExplorer(BitpayInsight):
    service_id = 124
    domain = "cashexplorer.bitcoin.com"
    supported_cryptos = ['bch']
    name = "Bitcoin.com BCH"
    version = 0.4


class BlockExplorerCash(BitpayInsight):
    service_id = 125
    domain = "bitcoincash.blockexplorer.com"
    supported_cryptos = ['bch']
    name = "BlockExplorer BCH"
    version = 0.4

class Litecore(BitpayInsight):
    service_id = 127
    domain = "insight.litecore.io"
    supported_cryptos = ['ltc']
    name = "Litecore (Insight)"
    version = 0.4

class TrezorBCH(BitpayInsight):
    service_id = 128
    domain = "bch-bitcore2.trezor.io"
    supported_cryptos = ['bch']
    name = "Trezor BCH Insight"
    version = 0.4

class BitpayInsightBCH(BitpayInsight):
    service_id = 129
    domain = "bch-insight.bitpay.com"
    supported_cryptos = ['bch']
    name = "Insight BCH (Bitpay)"
    version = 5

class EthPlorer(Service):
    service_id = 130

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://api.ethplorer.io/getAddressInfo/%s?apiKey=freekey" % address
        resp = self.get_url(url).json()
        if crypto.lower() == 'eth':
            return resp['ETH']['balance']
        for token in resp['tokens']:
            if token['tokenInfo']['symbol'] == crypto.upper():
                return token['balance']

class VertcoinInfo(Iquidus):
    service_id = 135
    base_url = "http://explorer.vertcoin.info"
    supported_cryptos = ['vtc']

class THCBlock(Iquidus):
    service_id = 136
    base_url = "http://thcblock.ga"
    supported_crypto = ['thc']

class Btgexp(Iquidus):
    service_id = 137
    base_url = "http://btgexp.com"
    supported_cryptos = ['btg']

class MonaInsight(BitpayInsight):
    service_id = 146
    domain = 'mona.chainsight.info'
    supported_crypto = ['mona']
    version = 0.2

class PrivateInsight(BitpayInsight):
    service_id = 147
    domain = "explorer.btcprivate.org"
    supported_crypto = ['btcp']
    version = 0.4

class BCCBlock(BitpayInsight):
    service_id = 149
    domain = "bccblock.info"
    supported_crypto = ['bch']
    version = 0.4

class DashBlockExplorer(BitpayInsight):
    service_id = 153
    domain = 'dashblockexplorer.com'
    supported_cryptos = ['dash']
    version = 0.4

class BCHSVExplorer(BitpayInsight):
    service_id = 154
    domain = 'bchsvexplorer.com'
    supported_cryptos = ['bsv']
    version = 0.4
