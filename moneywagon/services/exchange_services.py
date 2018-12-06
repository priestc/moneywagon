import json
import os

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

def make_standard_nonce(small=False):
    num = int(time.time() * 1000)
    if small:
        return str(num - 1506215312123)
    return str(num)

def make_stateful_nonce(exchange):
    path = os.path.expanduser('~/.moneywagon_state')
    if not os.path.exists(path):
        # make
        with open(path, "w+") as f:
            f.write('{}')

    with open(path) as f:
        j = json.loads(f.read())
        if exchange not in j:
            j[exchange] = {'last_used_nonce': 0}

        nonce = j[exchange].get('last_used_nonce', 0) + 1
        j[exchange]['last_used_nonce'] = nonce

    with open(path, "w") as f:
        f.write(json.dumps(j))

    return nonce

def eight_decimal_places(amount, format="str"):
    """
    >>> eight_decimal_places(3.12345678912345)
    "3.12345679"
    >>> eight_decimal_places("3.12345678912345")
    "3.12345679"
    >>> eight_decimal_places(3.12345678912345, format='float')
    3.12345679
    >>> eight_decimal_places("3.12345678912345", format='float')
    3.12345679
    """
    if type(amount) == str:
        return amount
    if format == 'str':
        return "%.8f" % amount
    if format == 'float':
        return float("%.8f" % amount)

class Bitstamp(Service):
    service_id = 1
    supported_cryptos = ['btc']
    api_homepage = "https://www.bitstamp.net/api/"
    name = "Bitstamp"
    exchange_fee_rate = 0.0025

    def __init__(self, customer_id=None, **kwargs):
        self.customer_id = customer_id
        super(Bitstamp, self).__init__(**kwargs)

    def make_market(self, crypto, fiat):
        return ("%s%s" % (crypto, fiat)).lower()

    def get_current_price(self, crypto, fiat):
        url = "https://www.bitstamp.net/api/v2/ticker/%s" % (
            self.make_market(crypto, fiat)
        )
        response = self.get_url(url).json()
        return float(response['last'])

    def get_pairs(self):
        return ['btc-usd', 'btc-eur', 'bch-btc', 'bch-usd', 'xrp-usd', 'xrp-eur', 'xrp-btc']

    def get_orderbook(self, crypto, fiat):
        url = "https://www.bitstamp.net/api/v2/order_book/%s/" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return {
            'bids': [(float(x[0]), float(x[1])) for x in resp['bids']],
            'asks': [(float(x[0]), float(x[1])) for x in resp['asks']]
        }

    def _make_signature(self, nonce):
        message = nonce + self.customer_id + self.api_key
        return hmac.new(
            self.api_secret,
            msg=message,
            digestmod=hashlib.sha256
        ).hexdigest().upper()

    def _auth_request(self, url, params):
        nonce = make_standard_nonce()
        params.update({
            'nonce': nonce,
            'signature': self._make_signature(nonce),
            'key': self.api_key,
        })
        return self.post_url(url, params)

    def get_exchange_balance(self, currency, type="available"):
        url = "https://www.bitstamp.net/api/balance/"
        resp = self._auth_request(url, {}).json()
        try:
            return float(resp["%s_%s" % (currency.lower(), type)])
        except KeyError:
            return 0

    def get_total_exchange_balances(self):
        url = "https://www.bitstamp.net/api/balance/"
        resp = self._auth_request(url, {}).json()
        return {
            code[:-8]: float(bal) for code, bal in resp.items()
            if code.endswith("balance") and float(bal) > 0
        }

    def get_deposit_address(self, currency):
        if currency.lower() == 'btc':
            url = "https://www.bitstamp.net/api/bitcoin_deposit_address/"
            return self._auth_request(url, {}).json()
        if currency.lower() == 'xrp':
            url = "https://www.bitstamp.net/api/ripple_address/"
            return self._auth_request(url, {}).json()['address']
        if currency.lower() in ['eth', 'ltc']:
            url = "https://www.bitstamp.net/api/v2/%s_address/" % currency.lower()
            return self._auth_request(url, {}).json()['address']

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        if type == 'limit':
            url = "https://www.bitstamp.net/api/v2/%s/%s/" % (
                side, self.make_market(crypto, fiat)
            )
            resp = self._auth_request(url, {
                'amount': eight_decimal_places(amount),
                'price': price,
            })
        if type == 'market':
            url = "https://www.bitstamp.net/api/v2/%s/market/%s/" % (
                side, self.make_market(crypto, fiat)
            )
            resp = self._auth_request(url, {
                'amount': eight_decimal_places(amount),
            })

        return resp.json()
    make_order.supported_types = ['limit', 'market']
    make_order.minimums = {}


class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = signature.digest().encode('base64').rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

class GDAX(Service):
    service_id = 59
    name = "GDAX"
    base_url = "https://api.gdax.com"
    api_homepage = "https://docs.gdax.com/"
    supported_cryptos = ['btc', 'ltc', 'eth', 'bch']
    exchange_fee_rate = 0.0025

    def __init__(self, api_pass=None, **kwargs):
        self.auth = None
        self.api_pass = api_pass

        super(GDAX, self).__init__(**kwargs)

        if self.api_key and self.api_secret and self.api_pass:
            self.auth = CoinbaseExchangeAuth(self.api_key, self.api_secret, self.api_pass)

    def check_error(self, response):
        if response.status_code != 200:
            j = response.json()
            raise ServiceError("GDAX returned %s error: %s" % (
                response.status_code, j['message'])
            )

        super(GDAX, self).check_error(response)

    def make_market(self, crypto, fiat):
        return ("%s-%s" % (crypto, fiat)).upper()

    def get_current_price(self, crypto, fiat):
        url = "%s/products/%s/ticker" % (self.base_url, self.make_market(crypto, fiat))
        response = self.get_url(url).json()
        return float(response['price'])

    def get_pairs(self):
        url = "%s/products" % self.base_url
        r = self.get_url(url).json()
        return [x['id'].lower() for x in r]

    def get_orderbook(self, crypto, fiat):
        url = "%s/products/%s/book?level=3" % (self.base_url, self.make_market(crypto, fiat))
        r = self.get_url(url).json()
        return {
            'bids': [(float(x[0]), float(x[1])) for x in r['bids']],
            'asks': [(float(x[0]), float(x[1])) for x in r['asks']]
        }

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        time_in_force = 'GTC'
        if type == 'fill-or-kill':
            type = 'limit'
            time_in_force = 'FOK'

        url = "%s/orders" % self.base_url
        data = {
            "size": eight_decimal_places(amount),
            "type": type,
            "price": price,
            "side": side,
            "time_in_force": time_in_force,
            "product_id": self.make_market(crypto, fiat)
        }
        response = self.post_url(url, json=data, auth=self.auth).json()
        return response['id']
    make_order.supported_types = ['fill-or-kill', 'limit', 'market', 'stop']
    make_order.minimums = {'btc': 0.0001, 'eth': 0.001, 'ltc': 0.01, 'usd': 1, 'eur': 1, 'gbp': 1}

    def list_orders(self, status="open"):
        url = "%s/orders" % self.base_url
        response = self.get_url(url, auth=self.auth)
        return response.json()

    def cancel_order(self, order_id):
        url = "%s/orders/%s" % (self.base_url, order_id)
        response = self.delete_url(url, auth=self.auth)
        return response.json()

    def get_exchange_balance(self, currency, type="available"):
        url = "%s/accounts" % self.base_url
        resp = self.get_url(url, auth=self.auth).json()
        try:
            match = [x for x in resp if currency.upper() == x['currency']][0]
        except IndexError:
            return 0
        return float(match[type])

    def get_total_exchange_balances(self):
        url = "%s/accounts" % self.base_url
        resp = self.get_url(url, auth=self.auth).json()
        return {
            x['currency'].lower(): float(x['balance']) for x in resp
        }

    def initiate_withdraw(self, currency, amount, address):
        url = "%s/withdrawals/crypto" % self.base_url
        resp = self.post_url(url, auth=self.auth, json={
            'crypto_address': address,
            'currency': currency.upper(),
            'amount': eight_decimal_places(amount)
        })
        return resp.json()

class BitFinex(Service):
    service_id = 120
    api_homepage = "https://bitfinex.readme.io/v2/reference"
    exchange_fee_rate = 0.002

    def check_error(self, response):
        j = response.json()
        if j and type(j) is list and j[0] == 'error':
            raise SkipThisService(
                "BitFinex returned Error: %s (%s)" % (j[2], j[1])
            )
        super(BitFinex, self).check_error(response)

    def parse_market(self, market):
        crypto = market[:3]
        fiat = market[3:]
        if crypto == 'dsh':
            crypto = 'dash'
        if crypto == 'iot':
            crypto = 'miota'
        return crypto, fiat

    def fix_symbol(self, symbol):
        if symbol == 'dash':
            return 'dsh'
        if symbol == 'miota':
            return 'iot'
        return symbol

    def make_market(self, crypto, fiat):
        return "%s%s" % (
            self.fix_symbol(crypto).lower(), self.fix_symbol(fiat).lower()
        )

    def get_pairs(self):
        url = "https://api.bitfinex.com/v1/symbols"
        r = self.get_url(url).json()
        return ["%s-%s" % self.parse_market(x) for x in r]

    def get_current_price(self, crypto, fiat):
        url = "https://api.bitfinex.com/v2/ticker/t%s" % self.make_market(crypto, fiat).upper()
        r = self.get_url(url).json()
        return r[6]

    def get_orderbook(self, crypto, fiat):
        url = "https://api.bitfinex.com/v1/book/%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return {
            'bids': [(float(x['price']), float(x['amount'])) for x in resp['bids']],
            'asks': [(float(x['price']), float(x['amount'])) for x in resp['asks']]
        }

    def _make_signature(self, path, args, nonce, version=2):
        if version == 2:
            msg = '/api/' + path + nonce + json.dumps(args)
        elif version == 1:
            msg = nonce # actually payload, but passed in as nonce
        return hmac.new(self.api_secret, msg, hashlib.sha384).hexdigest()

    def _auth_request(self, path, params):
        url = "https://api.bitfinex.com"
        nonce = make_standard_nonce()
        if path.startswith("/v2/"):
            headers = {
                'bfx-nonce': nonce,
                'bfx-apikey': self.api_key,
                'bfx-signature': self._make_signature(path, params, nonce, version=2)
            }
        elif path.startswith("/v1/"):
            params['request'] = path
            params['nonce'] = nonce
            payload = base64.b64encode(json.dumps(params))
            headers = {
                'X-BFX-PAYLOAD': payload,
                'X-BFX-APIKEY': self.api_key,
                'X-BFX-SIGNATURE': self._make_signature(path, params, payload, version=1)
            }
        return self.post_url(url + path, json=params, headers=headers)

    def get_deposit_address(self, crypto):
        resp = self._auth_request("/v2/auth/r/wallets", {})
        filt = [x[2] for x in resp.json() if x[1] == crypto.upper()]
        return filt[0] if filt else 0

    def get_exchange_balance(self, currency, type="available"):
        curr = self.fix_symbol(currency)
        resp = self._auth_request("/v1/balances", {}).json()
        for item in resp:
            if item['currency'] == curr.lower():
                return float(item[type])
        return 0

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        url = "/v1/order/new"
        resp = self._auth_request(url, {
            'symbol': self.make_market(crypto, fiat),
            'amount': eight_decimal_places(amount),
            'price': str(price),
            'side': side,
            'type': 'exchange %s' % type,
        })
        return resp.json()
    make_order.supported_types = ['fill-or-kill', 'market', 'limit', 'stop', 'trailing-stop']
    make_order.minimums = {}

    def initiate_withdraw(self, crypto, amount, address):
        from moneywagon.crypto_data import crypto_data
        if crypto == 'etc':
            type = "ethereumc"
        else:
            type = crypto_data[crypto.lower()]['name'].lower()
        resp = self._auth_request("/v1/withdraw", {
            "withdraw_type": type,
            "walletselected": "exchange",
            "amount": eight_decimal_places(amount),
            "address": address,
        }).json()
        return resp


class NovaExchange(Service):
    service_id = 89
    name = "NovaExchange"
    api_homepage = "https://novaexchange.com/remote/faq/"

    def make_market(self, crypto, fiat):
        return "%s_%s" % (fiat, crypto)

    def check_error(self, response):
        if response.json()['status'] == 'error':
            raise ServiceError("NovaExchange returned error: %s" % response.json()['message'])

        super(NovaExchange, self).check_error(response)

    def get_current_price(self, crypto, fiat):
        url = "https://novaexchange.com/remote/v2/market/info/%s" % self.make_market(crypto, fiat)
        r = self.get_url(url).json()
        return float(r['markets'][0]['last_price'])

    def get_pairs(self):
        url = "https://novaexchange.com/remote/v2/markets/"
        r = self.get_url(url).json()
        ret = []
        for pair in r['markets']:
            fiat = pair['basecurrency'].lower()
            crypto = pair['currency'].lower()
            ret.append("%s-%s" % (crypto, fiat))
        return ret

    def get_orderbook(self, crypto, fiat):
        url = "https://novaexchange.com/remote/v2/market/openorders/%s/both/" % (
            self.make_market(crypto, fiat)
        )
        r = self.get_url(url).json()
        return {
            'bids': [(float(x['price']), float(x['amount'])) for x in r['buyorders']],
            'asks': [(float(x['price']), float(x['amount'])) for x in r['sellorders']],
        }

    def _make_signature(self, url):
        return base64.b64encode(
            hmac.new(self.api_secret, url, hashlib.sha512).digest()
        )

    def _auth_request(self, url, params):
        url += '?nonce=' + make_standard_nonce()
        params['apikey'] = self.api_key
        params['signature'] = self._make_signature(url)
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        return self.post_url(url, data=params, headers=headers, timeout=60)

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        url = "https://novaexchange.com/remote/v2/private/trade/%s/" % (
            self.make_market(crypto, fiat)
        )
        params = {
            'tradetype': side.upper(),
            'tradeamount': eight_decimal_places(amount),
            'tradeprice': price,
            'tradebase': 0, # indicates "amount" is in crypto units, not fiat units
        }
        resp = self._auth_request(url, params)
        return resp.json()['tradeitems'][0]['orderid']
    make_order.minimums = {}

    def cancel_order(self, order_id):
        url = "https://novaexchange.com/remote/v2/private/cancelorder/%s/" % order_id
        resp = self._auth_request(url, {})
        return resp.json()['status'] == 'ok'

    def list_orders(self, status="open"):
        if status == 'open':
            url = "https://novaexchange.com/remote/v2/private/myopenorders/"
        else:
            NotImplementedError("getting orders by status=%s not implemented yet" % status)
        resp = self._auth_request(url, {})
        return resp.json()['items']

    def get_deposit_address(self, crypto):
        url = "https://novaexchange.com/remote/v2/private/getdepositaddress/%s/" % crypto
        resp = self._auth_request(url, {})
        return resp.json()['address']

    def initiate_withdraw(self, crypto, amount, address):
        url = "https://novaexchange.com/remote/v2/private/withdraw/%s/" % crypto
        params = {'currency': crypto, 'amount': eight_decimal_places(amount), 'address': address}
        resp = self._auth_request(url, params)
        return resp.json()


class xBTCe(Service):
    service_id = 90
    name = "xBTCe"
    api_homepage = "https://www.xbtce.com/tradeapi"

    def get_current_price(self, crypto, fiat):
        if crypto.lower() == 'dash':
            crypto = "dsh"
        if fiat.lower() == 'rur':
            fiat = 'rub'
        if fiat.lower() == 'cny':
            fiat = 'cnh'
        pair = "%s%s" % (crypto.upper(), fiat.upper())
        url = "https://cryptottlivewebapi.xbtce.net:8443/api/v1/public/ticker/%s" % pair
        r = self.get_url(url).json()
        try:
            return r[0]['LastSellPrice']
        except IndexError:
            raise ServiceError("Pair not found")

    def get_pairs(self):
        url = "https://cryptottlivewebapi.xbtce.net:8443/api/v1/public/symbol"
        r = self.get_url(url).json()
        ret = []
        for pair in r:
            crypto = pair['MarginCurrency'].lower()
            fiat = pair['ProfitCurrency'].lower()

            if crypto.lower() == 'dsh':
                crypto = "dash"
            if fiat.lower() == 'rub':
                fiat = 'rur'
            if fiat == 'cnh':
                fiat = 'cny'
            ret.append(("%s-%s" % (crypto, fiat)))

        return list(set(ret))


class OKcoin(Service):
    service_id = 60
    name = "OKcoin"
    exchange_base_url = "https://www.okcoin.cn"
    block_base_url = "http://block.okcoin.cn"
    supported_cryptos = ['btc', 'ltc']
    api_homepage = "https://www.okcoin.cn/rest_getStarted.html"

    def get_current_price(self, crypto, fiat):
        if not fiat == 'cny':
            raise SkipThisService("Only fiat=CNY supported")

        url = "%s/api/v1/ticker.do?symbol=%s_%s" % (
            self.exchange_base_url, crypto.lower(), fiat.lower()
        )
        response = self.get_url(url).json()
        return float(response['ticker']['last'])

    def check_error(self, response):
        j = response.json()
        if 'error_code' in j:
            raise ServiceError("OKcoin returned error code %s" % j['error_code'])

        super(OKcoin, self).check_error(response)

    def get_pairs(self):
        return ['btc-cny', 'ltc-cny']

    def get_block(self, crypto, block_hash=None, block_number=None, latest=False):
        if latest:
            args = 'latest_block.do?'

        if block_number or block_number == 0:
            args = "block_height.do?block_height=%s&" % block_number

        if block_hash:
            raise SkipThisService("Block by hash not supported")

        url = "%s/api/v1/%ssymbol=%s" % (
            self.block_base_url, args, crypto.upper()
        )
        r = self.get_url(url).json()

        ret = dict(
            block_number=r['height'],
            size=r['size'],
            time=arrow.get(r['time'] / 1000).datetime,
            hash=r['hash'],
            txids=r['txid'],
            tx_count=r['txcount'],
            version=r['version'],
            mining_difficulty=r['difficulty'],
            total_fees=r['fee'],
            sent_value=r['totalOut']
        )

        if r.get('relayed_by'):
            ret['miner'] = r['relayed_by']

        if r.get('previousblockhash'):
            ret['previous_hash'] = r['previousblockhash']

        if r.get('nextblockhash'):
            ret['next_hash'] = r['nextblockhash']

        return ret

class FreeCurrencyConverter(Service):
    service_id = 61
    base_url = "http://free.currencyconverterapi.com"
    api_homepage = "http://www.currencyconverterapi.com/docs"

    def get_fiat_exchange_rate(self, from_fiat, to_fiat):
        pair = "%s_%s" % (to_fiat.upper(), from_fiat.upper())
        url = "%s/api/v3/convert?q=%s&compact=y" % (
            self.base_url, pair
        )
        response = self.get_url(url).json()
        return response[pair]['val']


class BTCChina(Service):
    service_id = 62
    api_homepage = "https://www.btcc.com/apidocs/spot-exchange-market-data-rest-api#ticker"
    name = "BTCChina"

    def get_current_price(self, crypto, fiat):
        if fiat == 'usd':
            url = "https://spotusd-data.btcc.com/data/pro/ticker?symbol=%sUSD" % crypto.upper()
            key = "Last"
        else:
            url = "https://data.btcchina.com/data/ticker?market=%s%s" % (
                crypto.lower(), fiat.lower()
            )
            key = "last"
        response = self.get_url(url).json()
        if not response:
            raise ServiceError("Pair not supported (blank response)")
        return float(response['ticker'][key])


class Gemini(Service):
    service_id = 63
    api_homepage = "https://docs.gemini.com/rest-api/"
    name = "Gemini"
    exchange_fee_rate = 0.0025

    def check_error(self, response):
        j = response.json()
        if 'result' in j and j['result'] == 'error':
            raise ServiceError("Gemini returned error: %s" % j['reason'])

        super(Gemini, self).check_error(response)

    def make_market(self, crypto, fiat):
        return "%s%s" % (crypto.lower(), fiat.lower())

    def get_current_price(self, crypto, fiat):
        url = "https://api.gemini.com/v1/pubticker/%s" % self.make_market(crypto, fiat)
        response = self.get_url(url).json()
        return float(response['last'])

    def get_orderbook(self, crypto, fiat):
        url = "https://api.gemini.com/v1/book/%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return {
            'bids': [(float(x['price']), float(x['amount'])) for x in resp['bids']],
            'asks': [(float(x['price']), float(x['amount'])) for x in resp['asks']]
        }

    def _make_signature(self, payload):
        return hmac.new(self.api_secret, payload, hashlib.sha384).hexdigest()

    def _auth_request(self, path, params):
        params['nonce'] = make_standard_nonce()
        params['request'] = path
        payload = base64.b64encode(json.dumps(params))
        headers = {
            'X-GEMINI-APIKEY': self.api_key,
            'X-GEMINI-PAYLOAD': payload,
            'X-GEMINI-SIGNATURE': self._make_signature(payload)
        }
        return self.post_url("https://api.gemini.com" + path, headers=headers)

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        path = "/v1/order/new"
        #order_token = "" % datetime.datetime.now()
        opts = []

        if type == 'fill-or-kill':
            opts = ['immediate-or-cancel']
            type = "limit"

        if type == 'post-only':
            opts = ["maker-or-cancel"]
            type = 'limit'

        if type != "limit":
            raise NotImplementedError("Only limit orders currently supported")

        params = {
            #"client_order_id": order_token, # A client-specified order token
            "symbol": self.make_market(crypto, fiat), # Or any symbol from the /symbols api
            "amount": eight_decimal_places(amount), # Once again, a quoted number
            "price": str(price),
            "side": side, # must be "buy" or "sell"
            "type": "exchange %s" % type, # the order type; only "exchange limit" supported
            "options": opts # execution options; may be omitted for a standard limit order
        }
        resp = self._auth_request(path, params).json()
        return resp
    make_order.supported_types = ['post-only', 'limit', 'fill-or-kill']
    make_order.minimums = {}

    def get_deposit_address(self, currency):
        path = "/v1/deposit/%s/newAddress" % currency.lower()
        resp = self._auth_request(path, {})
        return resp.json()['address']

    def get_exchange_balance(self, currency, type="available"):
        path = "/v1/balances"
        resp = self._auth_request(path, {})
        try:
            match = [x for x in resp.json() if x['currency'] == currency.upper()][0]
        except IndexError:
            return 0
        return float(match[type])

    def get_total_exchange_balances(self):
        path = "/v1/balances"
        resp = self._auth_request(path, {})
        return {
            x['currency'].lower(): float(x['amount']) for x in resp.json()
            if float(x['amount']) > 0
        }


class CexIO(Service):
    service_id = 64
    api_homepage = "https://cex.io/rest-api"
    name = "Cex.io"
    exchange_fee_rate = 0.002

    def __init__(self, user_id=None, **kwargs):
        self.user_id = user_id
        super(CexIO, self).__init__(**kwargs)

    def check_error(self, response):
        super(CexIO, self).check_error(response)
        j = response.json()
        if 'error' in j:
            raise ServiceError("CexIO returned error: %s" % j['error'])

    def get_current_price(self, crypto, fiat):
        url = "https://cex.io/api/ticker/%s/%s" % (crypto.upper(), fiat.upper())
        response = self.get_url(url).json()
        return float(response['last'])

    def get_pairs(self):
        url = "https://cex.io/api/currency_limits"
        r = self.get_url(url).json()['data']['pairs']
        return [("%s-%s" % (x['symbol1'], x['symbol2'])).lower() for x in r]

    def get_orderbook(self, crypto, fiat):
        url = "https://cex.io/api/order_book/%s/%s/" % (crypto.upper(), fiat.upper())
        resp = self.get_url(url).json()
        return {
            'bids': [(x[0], x[1]) for x in resp['bids']],
            'asks': [(x[0], x[1]) for x in resp['asks']]
        }

    def _make_signature(self, nonce):
        message = nonce + self.user_id + self.api_key
        return hmac.new(self.api_secret, message, hashlib.sha256).hexdigest().upper()

    def _auth_request(self, url, params):
        nonce = make_standard_nonce()
        params['nonce'] = nonce
        params['signature'] = self._make_signature(nonce)
        params['key'] = self.api_key
        return self.post_url(url, params)

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        url = "https://cex.io/api/place_order/%s/%s" % (crypto.upper(), fiat.upper())
        if type in ('limit', 'market'):
            print("about to send amount to cex:", eight_decimal_places(amount))
            params = {
                'type': side,
                'amount': eight_decimal_places(amount),
            }
            if type == 'market':
                params['order_type'] = 'market'
            if type == 'limit':
                params['price'] = price
        else:
            raise Exception("Order with type=%s not yet supported" % type)

        resp = self._auth_request(url, params).json()
        return resp['id']
    make_order.supported_types = ['limit', 'market']
    make_order.minimums = {'btc': 0.01}

    def list_orders(self):
        url = "https://cex.io/api/open_orders/"
        resp = self._auth_request(url, {})
        return resp.json()

    def cancel_order(self, order_id):
        url = "https://cex.io/api/cancel_order/"
        resp = self._auth_request(url, {'id': order_id})
        return resp.content == 'true'

    def get_deposit_address(self, crypto):
        url = "https://cex.io/api/get_address"
        resp = self._auth_request(url, {'currency': crypto.upper()})
        return resp.json()['data']

    def get_exchange_balance(self, currency, type="available"):
        url = "https://cex.io/api/balance/"
        resp = self._auth_request(url, {})
        try:
            return float(resp.json()[currency.upper()]['available'])
        except KeyError:
            return 0

    def get_total_exchange_balances(self):
        url = "https://cex.io/api/balance/"
        resp = self._auth_request(url, {})
        return {
            code.lower(): float(data['available']) for code, data in resp.json().items()
            if code not in ['timestamp', 'username'] and float(data['available']) > 0
        }

class Poloniex(Service):
    service_id = 65
    api_homepage = "https://poloniex.com/support/api/"
    name = "Poloniex"
    exchange_fee_rate = 0.0025

    def check_error(self, response):
        j = response.json()
        if 'error' in j:
            raise ServiceError("Poloniex returned error: %s" % j['error'])

        super(Poloniex, self).check_error(response)

    def fix_symbol(self, symbol):
        symbol = symbol.lower()
        if symbol == 'usd':
            return 'usdt'
        if symbol == 'xlm':
            return 'str'
        return symbol

    def reverse_fix_symbol(self, symbol):
        symbol = symbol.lower()
        if symbol == 'usdt':
            return 'usd'
        if symbol == 'str':
            return 'xlm'
        return symbol

    def get_current_price(self, crypto, fiat):
        url = "https://poloniex.com/public?command=returnTicker"
        response = self.get_url(url).json()

        is_usd = False
        if fiat.lower() == 'usd':
            fiat = 'usdt'
            is_usd = True

        find_pair = "%s_%s" % (fiat.upper(), crypto.upper())
        for pair, data in response.items():
            if pair == find_pair:
                return float(data['last'])

        reverse_pair = "%s_%s" % (crypto.upper(), fiat.upper())
        for pair, data in response.items():
            if pair == reverse_pair:
                return 1 / float(data['last'])

        btc_pair = "BTC_%s" % crypto.upper()
        if is_usd and btc_pair in response:
            btc_rate = float(response['USDT_BTC']['last'])
            fiat_exchange = float(response[btc_pair]['last'])
            return fiat_exchange * btc_rate

        raise SkipThisService("Pair %s not supported" % find_pair)

    def get_pairs(self):
        url = "https://poloniex.com/public?command=returnTicker"
        r = self.get_url(url).json()
        ret = []
        for pair in r.keys():
            fiat, crypto = pair.lower().split('_')
            ret.append("%s-%s" % (self.reverse_fix_symbol(crypto), self.reverse_fix_symbol(fiat)))
        return ret

    def get_orderbook(self, crypto, fiat):
        url = "https://poloniex.com/public?command=returnOrderBook&currencyPair=%s" % (
            self.make_market(crypto, fiat)
        )
        resp = self.get_url(url).json()
        return {
            'asks': [(float(x[0]), x[1]) for x in resp['asks']],
            'bids': [(float(x[0]), x[1]) for x in resp['bids']]
        }

    def make_market(self, crypto, fiat):
        return ("%s_%s" % (self.fix_symbol(fiat), self.fix_symbol(crypto))).upper()

    def _make_signature(self, args):
        str_args = urlencode(args)
        return hmac.new(self.api_secret, str_args, hashlib.sha512).hexdigest()

    def _auth_request(self, args):
        url = "https://poloniex.com/tradingApi"
        args["nonce"] = make_standard_nonce()
        headers = {
            'Sign': self._make_signature(args),
            'Key': self.api_key
        }
        return self.post_url(url, args, headers=headers)

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        params = {}
        if type == "fill-or-kill":
            params = {'fillOrKill': 1}
        if type == 'post-only':
            params = {'postOnly': 1}
        params.update({
            "command": side,
            "currencyPair": self.make_market(crypto, fiat),
            "rate": price,
            "amount": eight_decimal_places(amount)
        })
        r = self._auth_request(params)
        return r.json()['orderNumber']
    make_order.supported_types = ['limit', 'fill-or-kill', 'post-only']
    make_order.minimums = {}

    def cancel_order(self, order_id):
        r = self._auth_request({
            "command": "cancelOrder",
            "orderNumber": order_id
        })
        return r['success'] == 1

    def list_orders(self, crypto=None, fiat=None):
        if not crypto and not fiat:
            pair = "all"
        else:
            self.make_market(crypto, fiat)

        resp = self._auth_request({
            "command": "returnOpenOrders",
            "currencyPair": pair,
        })
        return resp.json()

    def initiate_withdraw(self, crypto, amount, address):
        resp = self._auth_request({
            "command": "withdrawl",
            "currency": crypto,
            "amount": eight_decimal_places(amount),
            "address": address
        })
        return resp.json()

    def get_deposit_address(self, currency):
        c = self.fix_symbol(currency)
        resp = self._auth_request({"command": "returnDepositAddresses"})
        address = resp.json().get(c.upper())
        if not address:
            return self.generate_new_deposit_address(c)
        return address

    def generate_new_deposit_address(self, crypto):
        resp = self._auth_request({
            "command": "generateNewAddress",
            "currency": crypto.upper()
        })
        return resp.json()['response']

    def get_exchange_balance(self, currency, type="available"):
        resp = self._auth_request({"command": "returnBalances"})
        return float(resp.json().get(self.reverse_fix_symbol(currency).upper()))

    def get_total_exchange_balances(self):
        resp = self._auth_request({"command": "returnBalances"})
        return {
            self.reverse_fix_symbol(code): float(bal) for code, bal in resp.json().items()
            if float(bal) > 0
        }

class Bittrex(Service):
    service_id = 66
    api_homepage = "https://bittrex.com/home/api"
    exchange_fee_rate = 0.0025

    def check_error(self, response):
        j = response.json()
        if not j['success']:
            raise ServiceError("Bittrex returned error: %s" % j['message'])

        super(Bittrex, self).check_error(response)

    def fix_symbol(self, symbol):
        if symbol.lower() == 'usd':
            return 'usdt'

        if symbol == 'xmy':
            return 'myr'

        if symbol == 'bcc':
            raise SkipThisService("BCC not supported (maybe you want BCH?)")

        if symbol == 'bch':
            return 'bcc'

        return symbol.lower()

    def reverse_fix_symbol(self, symbol):
        symbol = symbol.lower()
        if symbol == 'usdt':
            return 'usd'
        if symbol == 'bcc':
            return 'bch'
        return symbol

    def make_market(self, crypto, fiat):
        return "%s-%s" % (
            self.fix_symbol(fiat).upper(),
            self.fix_symbol(crypto).upper()
        )

    def get_current_price(self, crypto, fiat):
        url = "https://bittrex.com/api/v1.1/public/getticker?market=%s" % (
            self.make_market(crypto, fiat)
        )
        r = self.get_url(url).json()
        return r['result']['Last']

    def get_orderbook(self, crypto, fiat):
        url = "https://bittrex.com/api/v1.1/public/getorderbook?market=%s&type=both" % (
            self.make_market(crypto, fiat)
        )
        r = self.get_url(url).json()['result']
        return {
            'bids': [(x['Rate'], x['Quantity']) for x in r['buy']],
            'asks': [(x['Rate'], x['Quantity']) for x in r['sell']],
        }

    def get_pairs(self):
        url = "https://bittrex.com/api/v1.1/public/getmarkets"
        r = self.get_url(url).json()['result']
        ret = []
        for x in r:
            crypto = x['MarketCurrency'].lower()
            fiat = x['BaseCurrency'].lower()
            if fiat == 'usdt':
                fiat = 'usd'
            ret.append("%s-%s" % (crypto, fiat))
        return ret

    def _make_signature(self, url):
        return hmac.new(
            self.api_secret.encode(), url.encode(), hashlib.sha512
        ).hexdigest()

    def _auth_request(self, path, params):
        if not self.api_key or not self.api_secret:
            raise Exception("Trade API requires an API key and secret.")
        params["apikey"] = self.api_key
        params["nonce"] = make_standard_nonce()
        url = "https://bittrex.com/api" + path + "?" + urlencode(params)
        return self.get_url(url, headers={"apisign": self._make_signature(url)})

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        path = "/v1.1/market/%slimit" % side
        r = self._auth_request(path, {
            'market': self.make_market(crypto, fiat),
            'quantity': eight_decimal_places(amount),
            'rate': price
        })
        return r.json()['result']['uuid']
    make_order.supported_types = ['limit']
    make_order.minimums = {}

    def cancel_order(self, order_id):
        path = "/v1.1/market/cancel"
        r = self._auth_request(path, {'uuid': order_id})
        return r['success']

    def get_exchange_balance(self, currency, type="available"):
        currency = self.fix_symbol(currency)
        path = "/v1.1/account/getbalance"
        resp = self._auth_request(path, {'currency': self.fix_symbol(currency)}).json()['result']
        return resp[type.capitalize()] or 0

    def get_total_exchange_balances(self):
        path = "/v1.1/account/getbalances"
        resp = self._auth_request(path, {}).json()['result']
        return {
            self.reverse_fix_symbol(x['Currency']): x['Balance'] for x in resp
            if x['Balance'] > 0
        }


    def get_deposit_address(self, crypto):
        path = "/v1.1/account/getdepositaddress"
        resp = self._auth_request(path, {'currency': self.fix_symbol(crypto)})
        return resp.json()['result']['Address']

    def initiate_withdraw(self, crypto, amount, address):
        path = "/v1.1/account/withdraw"
        resp = self._auth_request(path, {
            'currency': self.fix_symbol(crypto),
            'quantity': eight_decimal_places(amount),
            'address': address
        })
        return resp.json()


class Huobi(Service):
    service_id = 67
    api_homepage = "https://github.com/huobiapi/API_Docs_en/wiki"
    name = "Huobi"

    def check_error(self, response):
        if response.status_code != 200:
            j = response.json()
            raise ServiceError("Huobi returned error: %s" % j['error'])

        super(Huobi, self).check_error(response)

    def get_current_price(self, crypto, fiat):
        if fiat.lower() == "cny":
            fiat = 'static'
        elif fiat.lower() == 'usd':
            pass
        else:
            raise SkipThisService("CNY and USD only fiat supported")

        url = "http://api.huobi.com/%smarket/detail_%s_json.js" % (
            fiat.lower(), crypto.lower()
        )
        r = self.get_url(url).json()
        return r['p_last']


class BTER(Service):
    service_id = 25
    api_homepage = "https://bter.com/api"
    name = "BTER"

    def fix_symbol(self, symbol):
        if symbol == 'bch':
            return 'bcc'
        return symbol

    def make_market(self, crypto, fiat):
        return ("%s_%s" % (self.fix_symbol(crypto), fiat)).lower()

    def get_current_price(self, crypto, fiat):
        url = "http://data.bter.com/api/1/ticker/%s" % self.make_market(crypto, fiat)
        response = self.get_url(url).json()
        if response.get('result', '') == 'false':
            raise ServiceError("BTER returned error: " + r['message'])
        return float(response['last'] or 0)

    def get_pairs(self):
        url = "http://data.bter.com/api/1/pairs"
        r = self.get_url(url).json()
        return [x.replace("_", "-") for x in r]

    def get_orderbook(self, crypto, fiat):
        url = "http://data.bter.com/api2/1/orderBook/%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return {
            'bids': [(float(x[0]), float(x[1])) for x in resp['bids']],
            'asks': [(float(x[0]), float(x[1])) for x in resp['asks']],
        }

    def _make_signature(self, params):
        return hmac.new(
            self.api_secret, urlencode(params), hashlib.sha512
        ).hexdigest()

    def _auth_request(self, url, params):
        raise Exception("Not tested")
        return self.post_url(url, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Key': self.api_key,
            'Sign': self._make_signature(params)
        })

    def get_exchange_balance(self, currency, type="available"):
        url = "https://api.bter.com/api2/1/private/balances"
        resp = self._auth_request(url, {})
        for curr, bal in resp.json()[type].items():
            if curr == currency.upper():
                return float(bal)

    def get_deposit_address(self, currency):
        url = "https://bter.com/api2/1/private/depositAddress"
        resp = self._auth_request(url, {'currency': currency.upper()})
        return resp.json()['addr']


class Wex(Service):
    service_id = 7
    api_homepage = "https://wex.nz/api/documentation"
    name = "Wex"
    exchange_fee_rate = 0.002

    def check_error(self, response):
        try:
            j = response.json()
        except:
            raise ServiceError("Wex returned error: %s" % response.content)

        if 'error' in j:
            raise ServiceError("Wex returned error: %s" % j['error'])
        super(Wex, self).check_error(response)

    def make_market(self, crypto, fiat):
        return "%s_%s" % (
            self.fix_symbol(crypto).lower(),
            self.fix_symbol(fiat).lower()
        )

    def fix_symbol(self, symbol):
        if symbol == 'dash':
            return 'dsh'
        return symbol

    def reverse_fix_symbol(self, symbol):
        if symbol == 'dsh':
            return 'dash'
        return symbol

    def _fix_fiat_symbol(self, fiat):
        return fiat

    def get_current_price(self, crypto, fiat):
        pair = self.make_market(crypto, fiat)
        url = "https://wex.nz/api/3/ticker/" + pair
        response = self.get_url(url).json()
        return response[pair]['last']

    def get_pairs(self):
        url = "https://wex.nz/api/3/info"
        r = self.get_url(url).json()
        return [x.replace('_', '-') for x in r['pairs'].keys()]

    def get_orderbook(self, crypto, fiat):
        m = self.make_market(crypto, fiat)
        url = "https://wex.nz/api/3/depth/%s" % m
        resp = self.get_url(url).json()
        return {
            'bids': [(x[0], x[1]) for x in resp[m]['bids']],
            'asks': [(x[0], x[1]) for x in resp[m]['asks']]
        }

    def _make_signature(self, params):
        return hmac.new(
            self.api_secret, urlencode(params), hashlib.sha512
        ).hexdigest()

    def _auth_request(self, params):
        # max nonce wex will accept is 4294967294
        params['nonce'] = make_stateful_nonce(self.name)
        headers = {"Key": self.api_key, "Sign": self._make_signature(params)}
        return self.post_url("https://wex.nz/tapi", params, headers=headers)

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        params = {
            'method': 'Trade',
            'pair': self.make_market(crypto, fiat),
            'type': side,
            'rate': price,
            'amount': eight_decimal_places(amount),
        }
        return self._auth_request(params)
    make_order.supported_types = ['limit']
    make_order.minimums = {'btc': 0.001, 'ltc': 0.1}

    def get_deposit_address(self, crypto):
        params = {'coinName': crypto.lower(), 'method': 'CoinDepositAddress'}
        resp = self._auth_request(params).json()
        return resp['return']['address']

    def get_exchange_balance(self, currency, type="available"):
        resp = self._auth_request({'method': 'getInfo'}).json()
        try:
            return resp['return']['funds'][self.fix_symbol(currency).lower()]
        except IndexError:
            return 0

    def get_total_exchange_balances(self):
        resp = self._auth_request({'method': 'getInfo'}).json()['return']['funds']
        return {
            self.reverse_fix_symbol(code): bal for code, bal in resp.items()
            if not code.endswith("et") and bal > 0
        }

    def initiate_withdraw(self, currency, amount, address):
        resp = self._auth_request({
            'method': 'WithdrawCoin',
            'coinName': self.fix_symbol(currency),
            'amount': amount,
            'address': address,
        })
        return resp.json()


class ViaBTC(Service):
    service_id = 116

    def get_current_price(self, crypto, fiat):
        url = "https://www.viabtc.com/api/v1/market/ticker?market=%s%s" % (
            crypto.upper(), fiat.upper()
        )
        return float(self.get_url(url).json()['data']['ticker']['last'])


class CryptoDao(Service):
    service_id = 115
    api_homepage = "https://cryptodao.com/doc/api"

    def get_current_price(self, crypto, fiat):
        url = "https://cryptodao.com/api/ticker?source=%s&target=%s" % (
            fiat.upper(), crypto.upper()
        )
        r = self.get_url(url).json()
        return r['last']

    def get_orderbook(self, crypto, fiat):
        url = "https://cryptodao.com/api/depth?source=%s&target=%s" % (
            fiat.upper(), crypto.upper()
        )
        resp = self.get_url(url).json()
        return resp


class HitBTC(Service):
    service_id = 109
    api_homepage = "https://hitbtc.com/api"
    exchange_fee_rate = 0.001

    def check_error(self, response):
        j = response.json()

        if response.status_code in (400, 401) and 'error' in j:
            e = j['error']
            raise SkipThisService("HitBTC returned %s %s: %s" % (
                e['code'], e['message'], e['description']
            ))

        if 'code' in j:
            raise SkipThisService("HitBTC returned %s: %s" % (j['code'], j['message']))
        super(HitBTC, self).check_error(response)

    def fix_symbol(self, symbol):
        return symbol.lower()

    def make_market(self, crypto, fiat):
        return ("%s%s" % (self.fix_symbol(crypto), self.fix_symbol(fiat))).upper()

    def get_pairs(self):
        url = 'https://api.hitbtc.com/api/1/public/symbols'
        r = self.get_url(url).json()['symbols']
        return [("%s-%s" % (x['commodity'], x['currency'])).lower() for x in r]

    def get_current_price(self, crypto, fiat):
        url = "https://api.hitbtc.com/api/1/public/%s/ticker" % self.make_market(crypto, fiat)
        r = self.get_url(url).json()
        return float(r['last'])

    def get_orderbook(self, crypto, fiat):
        url = "https://api.hitbtc.com/api/1/public/%s/orderbook" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return {
            'asks': [(float(x[0]), float(x[1])) for x in resp['asks']],
            'bids': [(float(x[0]), float(x[1])) for x in resp['bids']]
        }

    def _auth_request(self, path, params, method="post"):
        path = path + "?" + urlencode({
            'nonce': make_standard_nonce(),
            'apikey': self.api_key
        })
        headers = {"X-Signature": self._make_signature(path, params)}
        return self._external_request(
            method, "https://api.hitbtc.com" + path,
            params, headers=headers
        )

    def _make_signature(self, path, params):
        msg = path + urlencode(params)
        return hmac.new(self.api_secret, msg, hashlib.sha512).hexdigest()

    def get_exchange_balance(self, currency, type="available"):
        resp = self._auth_request("/api/1/trading/balance", {}, method="get").json()
        c = self.fix_symbol(currency).upper()
        try:
            matched = [x for x in resp['balance'] if x['currency_code'] == c][0]
        except IndexError:
            return 0

        if type == 'available':
            return float(matched['cash'])

        raise NotImplemented()

    def get_total_exchange_balances(self):
        resp = self._auth_request("/api/1/trading/balance", {}, method="get")
        return {
            self.fix_symbol(x['currency_code']): float(x['cash'])
            for x in resp.json()['balance'] if float(x['cash']) > 0
        }

    def get_deposit_address(self, currency):
        path = "/api/1/payment/address/%s" % self.fix_symbol(currency).upper()
        resp = self._auth_request(path, {}, method="get").json()
        return resp['address']

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        path = "/api/1/trading/new_order"
        import random, string
        clientOrderId = "".join(random.choice(string.digits + string.ascii_lowercase) for _ in range(30))
        params = {
            'symbol': self.make_market(crypto, fiat),
            'side': side,
            'price': price,
            'quantity': eight_decimal_places(amount),
            'clientOrderId': clientOrderId
        }
        if type == 'fill-or-kill':
            params['timeInForce'] = 'FOK'

        resp = self._auth_request(path, params).json()
        return resp
    make_order.minimums = {}
    make_order.supported_types = ['fill-or-kill', 'limit']


class Liqui(Service):
    service_id = 106

    def parse_market(self, market):
        crypto, fiat = market.split("_")
        if fiat == 'usdt':
            fiat = 'usd'
        return crypto, fiat

    def get_pairs(self):
        url = "https://api.liqui.io/api/3/info"
        r = self.get_url(url).json()['pairs']
        return ["%s-%s" % self.parse_market(x) for x in r.keys()]

    def make_market(self, crypto, fiat):
        return "%s_%s" % (
            self.fix_symbol(crypto).lower(), self.fix_symbol(fiat).lower()
        )

    def fix_symbol(self, symbol):
        if symbol == 'usd':
            return 'usdt'
        return symbol

    def get_current_price(self, crypto, fiat):
        pair = self.make_market(crypto, fiat)
        url = "https://api.liqui.io/api/3/ticker/%s" % pair
        return self.get_url(url).json()[pair]['last']

    def get_orderbook(self, crypto, fiat):
        pair = self.make_market(crypto, fiat)
        url = "https://api.liqui.io/api/3/depth/%s" % pair
        return self.get_url(url).json()[pair]

    def _make_signature(self, params):
        return hmac.new(
            self.api_secret, "?" + urlencode(params), hashlib.sha512
        ).hexdigest()

    def _auth_request(self, params):
        params['nonce'] = make_standard_nonce(small=True)
        headers = {
            'Key':self.api_key,
            'Sign': self._make_signature(params)
        }
        return self.post_url('https://api.liqui.io', params, headers=headers)

    def get_exchange_balance(self, currency):
        resp = self._auth_request({'method': 'getInfo'}).json()
        return resp

    def list_orders(self, crypto=None, fiat=None):
        resp = self._auth_request({'method': 'ActiveOrders'}).json()
        return resp

class CoinOne(Service):
    service_id = 105

    def get_pairs(self):
        return ['btc-krw', 'eth-krw', 'xrp-krw', 'etc-krw']

    def get_current_price(self, crypto, fiat):
        url = "https://api.coinone.co.kr/ticker?currency=%s" % crypto.lower()
        return float(self.get_url(url).json()['last'])


class CryptoBG(Service):
    service_id = 102

    def get_current_price(self, crypto, fiat):
        url = "https://crypto.bg/api/v1/public_rates"
        if crypto != 'btc' or fiat != 'bgn':
            raise SkipThisService("Only btc-bgn supported")
        return float(self.get_url(url).json()['rates']['bitcoin']['bid'])


class Bitso(Service):
    service_id = 101

    def get_current_price(self, crypto, fiat):
        url = "https://api.bitso.com/v3/ticker/?book=%s_%s" % (crypto, fiat)
        r = self.get_url(url.lower()).json()
        return float(['payload']['last'])

    def get_pairs(self):
        url = "https://api.bitso.com/v3/available_books/"
        r = self.get_url(url).json()['payload']
        return [x['book'].replace("_", '-') for x in r]


class TradeSatoshi(Service):
    service_id = 96

    def get_pairs(self):
        url = "https://tradesatoshi.com/api/public/getmarketsummaries"
        r = self.get_url(url).json()
        return [x['market'].replace("_", '-').lower() for x in r['result']]

    def get_current_price(self, crypto, fiat):
        url = "https://tradesatoshi.com/api/public/getticker?market=%s_%s" % (
            crypto.upper(), fiat.upper()
        )
        return self.get_url(url).json()['result']['last']


class UseCryptos(Service):
    service_id = 95

    def get_pairs(self):
        url = "https://usecryptos.com/jsonapi/pairs"
        r = self.get_url(url).json()
        return r

    def get_current_price(self, crypto, fiat):
        pair = "%s-%s" % (crypto.lower(), fiat.lower())
        url = "https://usecryptos.com/jsonapi/ticker/%s" % pair
        return self.get_url(url).json()['lastPrice']


class BitcoinIndonesia(Service):
    service_id = 94
    api_homepage = "https://blog.bitcoin.co.id/wp-content/uploads/2014/03/API-Documentation-Bitcoin.co_.id_.pdf"

    def get_current_price(self, crypto, fiat):
        url = "https://vip.bitcoin.co.id/api/%s_%s/ticker" % (crypto.lower(), fiat.lower())
        return float(self.get_url(url).json()['ticker']['last'])

class Kraken(Service):
    service_id = 93

    def check_error(self, response):
        if response.json()['error']:
            raise ServiceError("Kraken returned error: %s" % response.json()['error'][0])

        super(Kraken, self).check_error(response)

    def get_pairs(self):
        url = "https://api.kraken.com/0/public/AssetPairs"
        r = self.get_url(url).json()['result']
        ret = []
        for name, data in r.items():
            crypto = data['base'].lower()
            if len(crypto) == 4 and crypto.startswith('x'):
                crypto = crypto[1:]
            fiat = data['quote'].lower()
            if fiat.startswith("z"):
                fiat = fiat[1:]
            if crypto == 'xbt':
                crypto = 'btc'
            if fiat == 'xxbt':
                fiat = 'btc'
            if fiat == 'xeth':
                fiat = 'eth'
            ret.append("%s-%s" % (crypto, fiat))
        return list(set(ret))

    def get_current_price(self, crypto, fiat):
        if crypto != 'bch':
            crypto = "x" + crypto.lower()
            if crypto == 'xbtc':
                crypto = 'xxbt'
            fiat = "z" + fiat.lower()
            if fiat == 'zbtc':
                fiat = 'xxbt'
        else:
            # bch pairs have completely different format for some reason
            # my god kraken's api is terrible
            if fiat.lower() == 'btc':
                fiat = 'xbt'

        pair = "%s%s" % (crypto.upper(), fiat.upper())
        url = "https://api.kraken.com/0/public/Ticker?pair=%s" % pair
        r = self.get_url(url).json()['result']
        return float(r[pair]['c'][0])


class BTC38(Service):
    service_id = 92
    api_homepage = "http://www.btc38.com/help/document/2581.html"

    def get_current_price(self, crypto, fiat):
        url = 'http://api.btc38.com/v1/ticker.php?c=%s&mk_type=%s' % (crypto, fiat)
        return self.get_url(url).json()['ticker']['last']

    def get_pairs(self):
        url = "http://api.btc38.com/v1/ticker.php?c=all&mk_type=cny"
        cny_bases = self.get_url(url).json().keys()

        url = "http://api.btc38.com/v1/ticker.php?c=all&mk_type=btc"
        btc_bases = self.get_url(url).json().keys()

        return ["%s-cny" % x for x in cny_bases] + ["%s-btc" % x for x in btc_bases]


class BleuTrade(Service):
    service_id = 91
    api_homepage = 'https://bleutrade.com/help/API'

    def get_pairs(self):
        url = 'https://bleutrade.com/api/v2/public/getmarkets'
        r = self.get_url(url).json()['result']
        return [x['MarketName'].lower().replace("_", '-') for x in r]

    def get_current_price(self, crypto, fiat):
        url = "https://bleutrade.com/api/v2/public/getticker?market=%s_%s" % (
            crypto.upper(), fiat.upper()
        )
        r = self.get_url(url).json()
        return float(r['result'][0]['Last'])



class xBTCe(Service):
    service_id = 90
    name = "xBTCe"
    api_homepage = "https://www.xbtce.com/tradeapi"

    def get_current_price(self, crypto, fiat):
        if crypto.lower() == 'dash':
            crypto = "dsh"
        if fiat.lower() == 'rur':
            fiat = 'rub'
        if fiat.lower() == 'cny':
            fiat = 'cnh'
        pair = "%s%s" % (crypto.upper(), fiat.upper())
        url = "https://cryptottlivewebapi.xbtce.net:8443/api/v1/public/ticker/%s" % pair
        r = self.get_url(url).json()
        try:
            return r[0]['LastSellPrice']
        except IndexError:
            raise ServiceError("Pair not found")

    def get_pairs(self):
        url = "https://cryptottlivewebapi.xbtce.net:8443/api/v1/public/symbol"
        r = self.get_url(url).json()
        ret = []
        for pair in r:
            crypto = pair['MarginCurrency'].lower()
            fiat = pair['ProfitCurrency'].lower()

            if crypto.lower() == 'dsh':
                crypto = "dash"
            if fiat.lower() == 'rub':
                fiat = 'rur'
            if fiat == 'cnh':
                fiat = 'cny'
            ret.append(("%s-%s" % (crypto, fiat)))

        return list(set(ret))


class Cryptopia(Service):
    service_id = 82
    api_homepage = "https://www.cryptopia.co.nz/Forum/Thread/255"
    exchange_fee_rate = 0.002

    def check_error(self, response):
        r = response.json()
        error = r.get('Error', False)
        if error is not None:
            raise ServiceError("Cryptopia returned error: %s" % r['Error'])
        super(Cryptopia, self).check_error(response)

    def fix_symbol(self, symbol):
        if symbol.lower() in ['nzd', 'usd']:
            symbol += "t"
        return symbol

    def reverse_fix_symbol(self, symbol):
        symbol = symbol.lower()
        if symbol in ['nzdt', 'usdt']:
            symbol = symbol[:-1]
        return symbol

    def make_market(self, crypto, fiat):
        return "%s_%s" % (
            self.fix_symbol(crypto).upper(), self.fix_symbol(fiat).upper()
        )

    def get_current_price(self, crypto, fiat):
        url = "https://www.cryptopia.co.nz/api/GetMarket/%s" % self.make_market(crypto, fiat)
        r = self.get_url(url).json()
        return r['Data']['LastPrice']

    def get_pairs(self):
        url = "https://www.cryptopia.co.nz/api/GetTradePairs"
        r = self.get_url(url).json()['Data']
        ret = []
        for pair in r:
            crypto = pair['Symbol']
            fiat = pair['BaseSymbol']
            if fiat.lower() == 'usdt':
                fiat = 'usd'
            ret.append(("%s-%s" % (crypto, fiat)).lower())

        return ret

    def get_orderbook(self, crypto, fiat):
        url = "https://www.cryptopia.co.nz/api/GetMarketOrders/%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return {
            'bids': [(x['Price'], x['Total']) for x in resp['Data']['Buy']],
            'asks': [(x['Price'], x['Total']) for x in resp['Data']['Sell']]
        }


    def _make_signature_header(self, url, params):
        nonce = str(int(time.time()))
        post_data = json.dumps(params);
        m = hashlib.md5()
        m.update(post_data)
        requestContentBase64String = base64.b64encode(m.digest())
        signature = self.api_key + "POST" + quote_plus(url).lower() + nonce + requestContentBase64String
        hmacsignature = base64.b64encode(
            hmac.new(base64.b64decode(self.api_secret), signature, hashlib.sha256).digest()
        )
        header_value = "amx " + self.api_key + ":" + hmacsignature + ":" + nonce
        return {'Authorization': header_value, 'Content-Type':'application/json; charset=utf-8' }

    def _auth_request(self, method, args):
        url = "https://www.cryptopia.co.nz/Api/" + method
        return self.post_url(url, json=args, headers=self._make_signature_header(url, args))

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        args = {
            'Market': ("%s/%s" % (self.fix_symbol(crypto), self.fix_symbol(fiat))).upper(),
            'Type': side,
            'Rate': price,
            'Amount': eight_decimal_places(amount)
        }
        resp = self._auth_request("SubmitTrade", args).json()
        return resp['Data']['OrderId']
    make_order.minimums = {}
    make_order.supported_types = ['limit']

    def get_exchange_balance(self, currency):
        curr = self.fix_symbol(currency).upper()
        try:
            resp = self._auth_request('GetBalance', {'Currency': curr})
        except ServiceError:
            return 0
        for item in resp.json()['Data']:
            if item['Symbol'] == curr:
                return item['Total']

    def get_total_exchange_balances(self):
        resp = self._auth_request('GetBalance', {}).json()
        #return resp.json()
        return {
            self.reverse_fix_symbol(x['Symbol']): x['Total'] for x in resp['Data']
            if x['Total'] > 0
        }

    def get_deposit_address(self, currency):
        curr = self.fix_symbol(currency).upper()
        resp = self._auth_request('GetDepositAddress', {'Currency': curr})
        return resp.json()['Data']['Address']

    def initiate_withdraw(self, currency, amount, address):
        curr = self.fix_symbol(currency).upper()
        resp = self._auth_request('SubmitWithdraw', {
            'Currency': curr,
            'Address': address,
            'Amount': amount
        })
        return resp.json()

class YoBit(Service):
    service_id = 77
    api_homepage = "https://www.yobit.net/en/api/"

    def get_current_price(self, crypto, fiat):
        pair = "%s_%s" % (crypto.lower(), fiat.lower())
        url = "https://yobit.net/api/3/ticker/%s" % pair
        r = self.get_url(url).json()

        if 'error' in r:
            raise SkipThisService(r['error'])

        return r[pair]['last']

    def get_pairs(self):
        url = 'https://yobit.net/api/3/info'
        r = self.get_url(url).json()
        return [x.replace("_", '-') for x in r['pairs'].keys()]


class Yunbi(Service):
    service_id = 78
    api_homepage = "https://yunbi.com/swagger"

    def get_current_price(self, crypto, fiat):
        if fiat.lower() != "cny":
            raise SkipThisService("Only CNY markets supported")
        url = "https://yunbi.com/api/v2/tickers/%s%s.json" % (crypto.lower(), fiat.lower())
        r = self.get_url(url, headers={"Accept": "application/json"}).json()
        return float(r['ticker']['last'])

    def get_pairs(self):
        url = "https://yunbi.com/api/v2/markets.json"
        r = self.get_url(url).json()
        ret = []
        for pair in r:
            ret.append(pair['name'].replace("/", '-').lower())
        return ret


class Vircurex(Service):
    service_id = 70
    base_url = "https://api.vircurex.com/api"
    api_homepage = "https://vircurex.com/welcome/api"

    def check_error(self, response):
        j = response.json()
        if j['status'] != 0:
            raise ServiceError("Vircurex returned error: %s" % j['status_text'])

        super(Vircurex, self).check_error(response)

    def get_current_price(self, crypto, fiat):
        if crypto == 'blk':
            crypto = 'bc'
        url = "%s/get_last_trade.json?base=%s&alt=%s" % (
            self.base_url, crypto.upper(), fiat.upper()
        )
        r = self.get_url(url).json()
        return float(r['value'])

    def get_pairs(self):
        url = "%s/get_info_for_currency.json" % self.base_url
        r = self.get_url(url).json()
        ret = []
        for fiat, data in r.items():
            if fiat == 'status':
                continue
            for crypto, exchange_data in data.items():
                pair = "%s-%s" % (crypto.lower(), fiat.lower())
                ret.append(pair)
        return ret


class LiveCoin(Service):
    service_id = 110
    base_url = "https://api.livecoin.net"
    api_homepage = "https://www.livecoin.net/api/public"

    def get_pairs(self):
        url = "%s/exchange/ticker" % (self.base_url)
        r = self.get_url(url).json()
        return [x['symbol'].replace('/', '-').lower() for x in r]

    def get_current_price(self, crypto, fiat):
        url = "%s/exchange/ticker/?currencyPair=%s/%s" % (
            self.base_url, crypto.upper(), fiat.upper()
        )
        return self.get_url(url).json()['last']

class Bithumb(Service):
    service_id = 129

    def get_current_price(self, crypto, fiat):
        if fiat != 'krw':
            raise SkipThisService("Only KRW supported")
        url = "https://api.bithumb.com/public/ticker/%s" % crypto.upper()
        resp = self.get_url(url).json()
        return float(resp['data']['average_price'])

    def get_orderbook(self, crypto, fiat):
        if fiat != 'krw':
            raise SkipThisService("Only KRW supported")

        url = "https://api.bithumb.com/public/orderbook/%s" % crypto
        resp =  self.get_url(url).json()['data']
        return {
            'bids': [(float(x['price']), float(x['quantity'])) for x in resp['bids']],
            'asks': [(float(x['price']), float(x['quantity'])) for x in resp['asks']]
        }

class Binance(Service):
    service_id = 130

    def check_error(self, response):
        j = response.json()
        if 'code' in j:
            raise ServiceError("Binance returned error: %s %s" % (j['code'], j['msg']))
        super(Binance, self).check_error(response)

    def make_market(self, crypto, fiat):
        return ("%s%s" % (self.fix_symbol(crypto), self.fix_symbol(fiat))).upper()

    def parse_market(self, market):
        market = market.lower()
        if market.endswith("usdt"):
            crypto, fiat = market[:-4], "usd"
        elif market.endswith("eth"):
            crypto, fiat = market[:-3], "eth"
        elif market.endswith("btc"):
            crypto, fiat = market[:-3], "btc"
        else:
            crypto, fiat = market[:-3], market[-3:]

        if crypto == 'iota':
            crypto = 'miota'

        if crypto == 'bcc':
            crypto = 'bch'

        return "%s-%s" % (crypto, fiat)

    def fix_symbol(self, symbol):
        if symbol.lower() == 'usd':
            return 'usdt'
        if symbol == 'miota':
            return 'iota'
        if symbol == 'bch':
            return "bcc"
        return symbol

    def get_current_price(self, crypto, fiat):
        url = "https://www.binance.com/api/v1/ticker/allPrices"
        resp = self.get_url(url).json()
        for data in resp:
            if data['symbol'] == self.make_market(crypto, fiat):
                return float(data['price'])
        raise SkipThisService("Market not found")

    def get_pairs(self):
        url = "https://www.binance.com/api/v1/ticker/allPrices"
        resp = self.get_url(url).json()
        symbols = []
        for data in resp:
            symbols.append(self.parse_market(data['symbol']))
        return symbols

    def get_orderbook(self, crypto, fiat):
        url = "https://www.binance.com/api/v1/depth"
        resp = self.get_url(url, {'symbol': self.make_market(crypto, fiat)}).json()
        return {
            'bids': [(float(x[1]), float(x[0])) for x in resp['bids']],
            'asks': [(float(x[1]), float(x[0])) for x in resp['asks']]
        }

    def _auth_request(self, path, params, method="post"):
        params['timestamp'] = make_standard_nonce()
        params['signature'] = self._make_signature(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        return self._external_request(
            method, "https://www.binance.com" + path, params, headers=headers
        )

    def _make_signature(self, params):
        return hmac.new(
            self.api_secret, urlencode(params), hashlib.sha256
        ).hexdigest()

    def get_exchange_balance(self, currency, type="available"):
        if type == 'available':
            type = 'free'
        else:
            type == 'locked'
        path = "/api/v3/account"
        resp = self._auth_request(path, {}, method="get").json()
        for data in resp['balances']:
            if data['asset'].lower() == currency.lower():
                return float(data[type])

        return 0


class BitFlyer(Service):
    service_id = 111
    api_homepage = "https://bitflyer.jp/API?top_link&footer"

    def get_current_price(self, crypto, fiat):
        url = "https://api.bitflyer.jp/v1/getticker?product_code=%s" % (
            self.make_market(crypto, fiat)
        )
        r = self.get_url(url).json()
        return r['ltp']

    def get_pairs(self):
        return ['btc-jpy', 'eth-btc', 'btc-usd']

    def make_market(self, crypto, fiat):
        return ("%s_%s" % (crypto, fiat)).upper()

    def get_orderbook(self, crypto, fiat):
        if fiat.lower() == 'jpy':
            domain = "api.bitflyer.jp"
        elif fiat.lower() == 'usd':
            domain = "api.bitflyer.com"
        else:
            raise SkipThisService("Only jpy and usd suppported")
        url = "https://%s/v1/getboard?product_code=%s" % (
            domain, self.make_market(crypto, fiat)
        )
        resp = self.get_url(url).json()
        return {
            'bids': [(x['price'], x['size']) for x in resp['bids']],
            'asks': [(x['price'], x['size']) for x in resp['asks']],
        }

    def get_block(self, crypto, block_number=None, block_hash=None, latest=False):
        url = "https://chainflyer.bitflyer.jp/v1/block/%s" % (
            block_hash or
            ('height/%s' % block_number if block_number else None) or
            ('latest' if latest else 'None')
        )
        r = self.get_url(url).json()
        return dict(
            block_number=r['height'],
            time=arrow.get(r['timestamp']).datetime,
            #mining_difficulty=r['difficulty'],
            hash=r['block_hash'],
            next_hash=r.get('nextblockhash', None),
            previous_hash=r.get('prev_block'),
            txids=r['tx_hashes'],
            version=r['version']
        )

class BitX(Service):
    service_id = 131
    api_homepage = "https://www.luno.com/en/api"

    def parse_market(self, market):
        if market.startswith("XBT"):
            crypto = "BTC"
            fiat = market[3:]
        return crypto, fiat

    def fix_symbol(self, symbol):
        if symbol.lower() == 'btc':
            return 'XBT'
        return symbol

    def make_market(self, crypto, fiat):
        return ("%s%s" % (self.fix_symbol(crypto), self.fix_symbol(fiat))).upper()

    def get_current_price(self, crypto, fiat):
        url = "https://api.mybitx.com/api/1/ticker?pair=%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return float(resp['last_trade'])

    def get_pairs(self):
        url = "https://api.mybitx.com/api/1/tickers"
        resp = self.get_url(url).json()['tickers']
        return [
            ("%s-%s" % self.parse_market(x['pair'])).lower() for x in resp
        ]

    def get_orderbook(self, crypto, fiat):
        url = "https://api.mybitx.com/api/1/orderbook?pair=%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return {
            'bids': [(float(x['price']), float(x['volume'])) for x in resp['bids']],
            'asks': [(float(x['price']), float(x['volume'])) for x in resp['asks']]
        }

class ItBit(Service):
    service_id = 132

    def fix_symbol(self, symbol):
        if symbol.lower() == 'btc':
            return 'XBT'
        return symbol

    def make_market(self, crypto, fiat):
        return ("%s%s" % (self.fix_symbol(crypto), self.fix_symbol(fiat))).upper()

    def get_current_price(self, crypto, fiat):
        url = "https://api.itbit.com/v1/markets/%s/ticker" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return float(resp['lastPrice'])

    def get_pairs(self):
        return ['btc-usd', 'btc-sgd', 'btc-eur']

    def get_orderbook(self, crypto, fiat):
        url = "https://api.itbit.com/v1/markets/%s/order_book" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return {
            'bids': [(float(x[0]), float(x[1])) for x in resp['bids']],
            'asks': [(float(x[0]), float(x[1])) for x in resp['asks']]
        }

    def _make_signature(self):
        pass # https://github.com/itbit/itbit-restapi-python/blob/master/itbit_api.py

class KuCoin(Service):
    service_id = 133
    symbol_mapping = (
        ('usd', 'usdt'),
    )

    def make_market(self, crypto, fiat):
        return ("%s-%s" % (self.fix_symbol(crypto), self.fix_symbol(fiat))).upper()

    def parse_market(self, market):
        return super(KuCoin, self).parse_market(market.lower(), '-')

    def get_pairs(self):
        url = "https://api.kucoin.com/v1/market/open/symbols"
        resp = self.get_url(url).json()
        pairs = []
        for pair in resp['data']:
            crypto, fiat = self.parse_market(pair['symbol'])
            pairs.append("%s-%s" % (crypto, fiat))
        return pairs

    def get_orderbook(self, crypto, fiat):
        url = "https://api.kucoin.com/v1/open/orders?symbol=%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()['data']
        return {
            'bids': [(x[0], x[1]) for x in resp['BUY']],
            'asks': [(x[0], x[1]) for x in resp['SELL']]
        }

    def get_current_price(self, crypto, fiat):
        url = "https://api.kucoin.com/v1/open/tick?symbol=%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()['data']
        return resp['lastDealPrice']

class CCex(Service):
    service_id = 134
    api_homepage = "https://c-cex.com/?id=api"
    base_url = "https://c-cex.com/t/api_pub.html"

    def check_error(self, response):
        if response.content == "Maintenance...":
            raise ServiceError("C-Cex is down for maintenance")
        super(CCex, self).check_error(response)

    def make_market(self, crypto, fiat):
        return "%s-%s" % (crypto.lower(), fiat.lower())

    def get_current_price(self, crypto, fiat):
        url = "https://c-cex.com/t/%s.json" % (
            self.make_market(crypto, fiat)
        )
        response = self.get_url(url).json()
        return float(response['ticker']['lastprice'])

    def get_pairs(self):
        url = "https://c-cex.com/t/pairs.json"
        r = self.get_url(url).json()
        return r['pairs']

    def get_orderbook(self, crypto, fiat):
        url = "%s?a=getorderbook&market=%s&type=both" % (
            self.base_url, self.make_market(crypto, fiat)
        )
        resp = self.get_url(url).json()['result']
        return {
            'bids': [(x["Rate"], x["Quantity"]) for x in resp['buy']],
            'asks': [(x["Rate"], x["Quantity"]) for x in resp['sell']]
        }

    def _auth_request(self, params):
        params['nonce'] = make_standard_nonce()
        params['apikey'] = self.api_key
        url = "%s?%s" % (self.base_url, urlencode(params))
        headers = {'apisign': self._make_signature(url)}
        return self.get_url(url, headers=headers)

    def _make_signature(self, url):
        return hmac.new(
            self.api_secret,
            msg=url,
            digestmod=hashlib.sha512
        ).hexdigest()

    def get_exchange_balance(self, currency, type="available"):
        resp = self._auth_request({'a': 'getbalance', 'currency': currency})
        if type == 'available':
            return resp.json()['Available']

    def get_deposit_address(self, currency):
        resp = self._auth_request({'a': 'getbalance', 'currency': currency})
        return resp.json()['CryptoAddress']

class CoinEx(Service):
    service_id = 138

    def __init__(self, access_id=None, **kwargs):
        self.access_id = access_id
        return super(CoinEx, self).__init__(**kwargs)

    def get_pairs(self):
        url = "https://api.coinex.com/v1/market/list"
        resp = self.get_url(url).json()['data']
        return [("%s-%s" % (x[:-3], x[-3:])).lower() for x in resp]

    def make_market(self, crypto, fiat):
        return ("%s%s" % (crypto, fiat)).upper()

    def get_current_price(self, crypto, fiat):
        url = "https://api.coinex.com/v1/market/ticker?market=%s" % (
            self.make_market(crypto, fiat)
        )
        resp = self.get_url(url).json()
        return float(resp['data']['ticker']['last'])

    def _auth_request(self, url, params=None):
        params['tonce'] = make_standard_nonce()
        params['access_id'] = self.access_id
        str_params = urlencode(sorted(params.items(), key=lambda x: x[0]))
        to_sign = str_params + "&secret_key=%s" % self.api_secret
        digest = hashlib.md5(to_sign).hexdigest().upper()
        return self.get_url(url + "?" + str_params, headers={
            'Content-Type': 'application/json',
            'authorization': digest
        })

    def get_exchange_balance(self, crypto):
        url = "https://api.coinex.com/v1/balance/"
        resp = self._auth_request(url, {}).json()
        return resp


class OKEX(Service):
    service_id = 139
    api_homepage = 'https://www.okex.com/rest_api.html'
    symbol_mapping = (
        ('usd', 'usdt'),
    )

    def check_error(self, response):
        j = response.json()
        if 'error_code' in j:
            raise ServiceError("OKEX returned error: %s" % j['error_code'])
        super(OKEX, self).check_error(response)

    def get_current_price(self, crypto, fiat):
        url = "https://www.okex.com/api/v1/ticker.do?symbol=%s" % (
            self.make_market(crypto, fiat)
        )
        resp = self.get_url(url).json()
        return float(resp['ticker']['last'])

class BitZ(Service):
    service_id = 140

    def check_error(self, response):
        j = response.json()
        if not j['code'] == 0:
            raise ServiceError("BitZ returned error: %s: %s" % (
                j['code'], j['msg']
            ))
        super(BitZ, self).check_error(response)

    def get_current_price(self, crypto, fiat):
        url = "https://www.bit-z.com/api_v1/ticker?coin=%s" % (self.make_market(crypto, fiat))
        resp = self.get_url(url).json()
        return float(resp['data']['last'])

class Zaif(Service):
    service_id = 141

    def check_error(self, response):
        j = response.json()
        if 'error' in j:
            raise ServiceError("Zaif returned error: %s" % (j['error']))
        super(Zaif, self).check_error(response)

    def get_current_price(self, crypto, fiat):
        url = "https://api.zaif.jp/api/1/ticker/%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return resp['last']

class Korbit(Service):
    service_id = 142
    api_homepage = "https://apidocs.korbit.co.kr/"

    def get_current_price(self, crypto, fiat):
        url = "https://api.korbit.co.kr/v1/ticker?currency_pair=%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return float(resp['last'])

    def get_orderbook(self, crypto, fiat):
        url = "https://api.korbit.co.kr/v1/orderbook?currency_pair=%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return {
            'asks': [(float(x[0]), float(x[1])) for x in resp['asks']],
            'bids': [(float(x[0]), float(x[1])) for x in resp['bids']]
        }

class CoinEgg(Service):
    service_id = 143
    api_homepage = "https://www.coinegg.com/explain.api.html#partone"

    def get_current_price(self, crypto, fiat):
        if fiat.lower() != 'btc':
            raise SkipThisService("Only BTC markets supported")
        url = "https://api.coinegg.com/api/v1/ticker/?coin=%s" % crypto
        resp = self.get_url(url).json()
        return float(resp['last'])

    def get_orderbook(self, crypto, fiat):
        if fiat.lower() != 'btc':
            raise SkipThisService("Only BTC markets supported")

        url = "https://api.coinegg.com/api/v1/depth/"
        resp = self.get_url(url).json()
        return {
            'bids': [(float(x[0]), float(x[1])) for x in resp['bids']],
            'asks': [(float(x[0]), float(x[1])) for x in resp['asks']]
        }

class ZB(Service):
    service_id = 144
    api_homepage = "https://www.zb.com/i/developer"
    symbol_mapping = (
        ('usd', 'usdt'),
        ('bch', 'bcc')
    )

    def get_pairs(self):
        url = "http://api.zb.com/data/v1/markets"
        resp = self.get_url(url).json()
        pairs = []
        for pair in resp.keys():
            pairs.append("%s-%s" % self.parse_market(pair))
        return pairs

    def get_current_price(self, crypto, fiat):
        url = "http://api.zb.com/data/v1/ticker?market=%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return float(resp['ticker']['last'])

    def get_orderbook(self, crypto, fiat):
        url = "http://api.zb.com/data/v1/depth?market=%s&size=3" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        del resp['timestamp']
        return resp

class CoinNest(Service):
    service_id = 145
    api_homepage = "https://www.coinnest.co.kr/doc/intro.html"

    def get_current_price(self, crypto, fiat):
        if fiat.lower() != 'krw':
            raise SkipThisService("Only KRW markets supported")
        url = "https://api.coinnest.co.kr/api/pub/ticker?coin=%s" % crypto
        resp = self.get_url(url).json()
        return resp['last']

    def get_orderbook(self, crypto, fiat):
        if fiat.lower() != 'krw':
            raise SkipThisService("Only KRW markets supported")
        url = "https://api.coinnest.co.kr/api/pub/depth?coin=%s" % crypto
        resp = self.get_url(url).json()
        del resp['result']
        return resp

class BitBank(Service):
    service_id = 147
    api_homepage = "https://docs.bitbank.cc/"
    symbol_mapping = (
        ('bch', 'bcc'),
    )

    def get_current_price(self, crypto, fiat):
        url = "https://public.bitbank.cc/%s/ticker" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return float(resp['data']['last'])

    def get_orderbook(self, crypto, fiat):
        url = "https://public.bitbank.cc/%s/depth" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return {
            'asks': [(float(x[0]), float(x[1])) for x in resp['data']['asks']],
            'bids': [(float(x[0]), float(x[1])) for x in resp['data']['bids']]
        }

class EXX(Service):
    service_id = 148
    symbol_mapping = (
        ('usd', 'usdt'),
        ('bch', 'bcc')
    )

    def get_pairs(self):
        url = "https://api.exx.com/data/v1/markets"
        resp = self.get_url(url).json()
        pairs = []
        for pair in resp.keys():
            pairs.append("%s-%s" % self.parse_market(pair))
        return pairs

    def get_current_price(self, crypto, fiat):
        url = "https://api.exx.com/data/v1/ticker?currency=%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return float(resp['ticker']['last'])

    def get_orderbook(self, crypto, fiat):
        url = "https://api.exx.com/data/v1/depth?currency=%s" % self.make_market(crypto, fiat)
        resp = self.get_url(url).json()
        return {
            'asks': [(float(x[0]), float(x[1])) for x in resp['asks']],
            'bids': [(float(x[0]), float(x[1])) for x in resp['bids']]
        }

class BL3P(Service):
    service_id = 150

    def check_error(self, response):
        j = response.json()
        if j['result'] == 'error':
            d = j['data']
            raise ServiceError("BL3P returned error: %s, %s" % (d['code'], d['message']))
        super(BL3P, self).check_error(response)

    def get_current_price(self, crypto, fiat):
        url = "https://api.bl3p.eu/1/%s/ticker" % self.make_market(crypto, fiat, '-')
        return self.get_url(url).json()

class BTCbox(Service):
    service_id = 151

    def get_current_price(self, crypto, fiat):
        if fiat.lower() != 'jpy':
            raise SkipThisService("Only JPY trading pairs supported")
        url = "https://www.btcbox.co.jp/api/v1/ticker/?coin=%s" % crypto
        r = self.get_url(url).json()
        return r['last']

class Bibox(Service):
    service_id = 152
    api_homepage = "https://github.com/Biboxcom/api_reference/wiki/api_reference"
    symbol_mapping = (
        ('usd', 'usdt'),
    )

    def get_current_price(self, crypto, fiat):
        url = "https://api.bibox.com/v1/mdata?cmd=ticker&pair=%s" % (
            self.make_market(crypto, fiat).upper()
        )
        r = self.get_url(url).json()
        return float(r['result']['last'])

    def get_pairs(self):
        url ="https://api.bibox.com/v1/mdata?cmd=pairList"
        r = self.get_url(url).json()
        markets = []
        for data in r['result']:
            pair = data['pair']
            crypto, fiat = self.parse_market(pair)
            markets.append("%s-%s" % (crypto, fiat))
        return markets

    def get_orderbook(self, crypto, fiat):
        url = "https://api.bibox.com/v1/mdata?cmd=depth&pair=%s&size=200" % (
            self.make_market(crypto, fiat).upper()
        )
        resp = self.get_url(url).json()['result']
        return {
            'asks': [(float(x['price']), float(x['volume'])) for x in resp['asks']],
            'bids': [(float(x['price']), float(x['volume'])) for x in resp['bids']]
        }
