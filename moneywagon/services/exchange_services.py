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

def make_standard_nonce(small=False):
    num = int(time.time() * 1000)
    if small:
        return str(num - 1506215312123)
    return str(num)

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

    def __init__(self, api_key=None, api_secret=None, customer_id=None, **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
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
        return ['btc-usd', 'btc-eur', 'xrp-usd', 'xrp-eur', 'xrp-btc']

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

    def _trade_api(self, url, params):
        nonce = make_standard_nonce()
        params.update({
            'nonce': nonce,
            'signature': self._make_signature(nonce),
            'key': self.api_key,
        })
        return self.post_url(url, params)

    def get_exchange_balance(self, currency, type="available"):
        url = "https://www.bitstamp.net/api/balance/"
        resp = self._trade_api(url, {}).json()
        return float(resp["%s_%s" % (currency.lower(), type)])

    def get_deposit_address(self, currency):
        if currency.lower() == 'btc':
            url = "https://www.bitstamp.net/api/bitcoin_deposit_address/"
            return self._trade_api(url, {}).json()
        if currency.lower() == 'xrp':
            url = "https://www.bitstamp.net/api/ripple_address/"
            return self._trade_api(url, {}).json()['address']
        if currency.lower() in ['eth', 'ltc']:
            url = "https://www.bitstamp.net/api/v2/%s_address/" % currency.lower()
            return self._trade_api(url, {}).json()['address']


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
    supported_cryptos = ['btc', 'ltc', 'eth']
    exchange_fee_rate = 0.0025

    def __init__(self, api_key=None, api_secret=None, api_pass=None, **kwargs):
        self.auth = None
        self.api_key = api_key
        self.api_secret = api_secret
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

    def get_current_price(self, crypto, fiat):
        url = "%s/products/%s-%s/ticker" % (self.base_url, crypto.upper(), fiat.upper())
        response = self.get_url(url).json()
        return float(response['price'])

    def get_pairs(self):
        url = "%s/products" % self.base_url
        r = self.get_url(url).json()
        return [x['id'].lower() for x in r]

    def get_orderbook(self, crypto, fiat):
        url = "%s/products/%s-%s/book?level=3" % (self.base_url, crypto.upper(), fiat.upper())
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
            "product_id": "%s-%s" % (crypto.upper(), fiat.upper())
        }
        response = self.post_url(url, json=data, auth=self.auth).json()
        return response['id']
    make_order.supported_types = ['fill-or-kill', 'limit', 'market', 'stop']
    make_order.minimums = {}

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
        return float(match['available'])


class BitFinex(Service):
    service_id = 120
    api_homepage = "https://bitfinex.readme.io/v2/reference"
    exchange_fee_rate = 0.002

    def __init__(self, api_key=None, api_secret=None, **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
        super(BitFinex, self).__init__(**kwargs)

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

    def _trade_api(self, path, params):
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
        resp = self._trade_api("/v2/auth/r/wallets", {})
        filt = [x[2] for x in resp.json() if x[1] == crypto.upper()]
        return filt[0] if filt else 0

    def get_exchange_balance(self, currency, type="available"):
        resp = self._trade_api("/v1/balances", {}).json()
        try:
            matched = [x for x in resp if x['currency'] == currency.lower()][0]
        except IndexError:
            return 0
        return float(matched[type])

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        url = "/v1/order/new"
        resp = self._trade_api(url, {
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
        resp = self._trade_api("/v1/withdraw", {
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

    def __init__(self, api_key=None, api_secret=None, **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
        super(NovaExchange, self).__init__(**kwargs)

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

    def _trade_api(self, url, params):
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
        resp = self._trade_api(url, params)
        return resp.json()['tradeitems'][0]['orderid']
    make_order.minimums = {}

    def cancel_order(self, order_id):
        url = "https://novaexchange.com/remote/v2/private/cancelorder/%s/" % order_id
        resp = self._trade_api(url, {})
        return resp.json()['status'] == 'ok'

    def list_orders(self, status="open"):
        if status == 'open':
            url = "https://novaexchange.com/remote/v2/private/myopenorders/"
        else:
            NotImplementedError("getting orders by status=%s not implemented yet" % status)
        resp = self._trade_api(url, {})
        return resp.json()['items']

    def get_deposit_address(self, crypto):
        url = "https://novaexchange.com/remote/v2/private/getdepositaddress/%s/" % crypto
        resp = self._trade_api(url, {})
        return resp.json()['address']

    def initiate_withdraw(self, crypto, amount, address):
        url = "https://novaexchange.com/remote/v2/private/withdraw/%s/" % crypto
        params = {'currency': crypto, 'amount': eight_decimal_places(amount), 'address': address}
        resp = self._trade_api(url, params)
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

    def _trade_api(self, path, params):
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
        resp = self._trade_api(path, params).json()
        return resp
    make_order.supported_types = ['post-only', 'limit', 'fill-or-kill']
    make_order.minimums = {}

    def get_deposit_address(self, currency):
        path = "/v1/deposit/%s/newAddress" % currency.lower()
        resp = self._trade_api(path, {})
        return resp.json()['address']

    def get_exchange_balance(self, currency, type="available"):
        path = "/v1/balances"
        resp = self._trade_api(path, {})
        try:
            match = [x for x in resp.json() if x['currency'] == currency.upper()][0]
        except IndexError:
            return 0
        return float(match[type])


class CexIO(Service):
    service_id = 64
    api_homepage = "https://cex.io/rest-api"
    name = "Cex.io"
    exchange_fee_rate = 0.002

    def __init__(self, api_key=None, api_secret=None, user_id=None, **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
        self.user_id = user_id
        super(CexIO, self).__init__(**kwargs)

    def check_error(self, response):
        super(CexIO, self).check_error(response)
        j = response.json()
        if 'error' in j:
            raise ServiceError("CexIO returned error: %s" % j['error'])

    def get_current_price(self, crypto, fiat):
        url = "https://c-cex.com/t/%s-%s.json" % (
            crypto.lower(), fiat.lower()
        )
        response = self.get_url(url).json()
        return float(response['ticker']['lastprice'])

    def get_pairs(self):
        url = "https://c-cex.com/t/pairs.json"
        r = self.get_url(url).json()
        return r['pairs']

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

    def _trade_api(self, url, params):
        nonce = make_standard_nonce()
        params['nonce'] = nonce
        params['signature'] = self._make_signature(nonce)
        params['key'] = self.api_key
        return self.post_url(url, params)

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        url = "https://cex.io/api/place_order/%s/%s" % (crypto.upper(), fiat.upper())
        if type in ('limit', 'market'):
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

        resp = self._trade_api(url, params).json()
        return resp['id']
    make_order.supported_types = ['limit', 'market']
    make_order.minimums = {}

    def list_orders(self):
        url = "https://cex.io/api/open_orders/"
        resp = self._trade_api(url, {})
        return resp.json()

    def cancel_order(self, order_id):
        url = "https://cex.io/api/cancel_order/"
        resp = self._trade_api(url, {'id': order_id})
        return resp.content == 'true'

    def get_deposit_address(self, crypto):
        url = "https://cex.io/api/get_address"
        resp = self._trade_api(url, {'currency': crypto.upper()})
        return resp.json()['data']

    def get_exchange_balance(self, currency, type="available"):
        url = "https://cex.io/api/balance/"
        resp = self._trade_api(url, {})
        try:
            return float(resp.json()[currency.upper()]['available'])
        except KeyError:
            return 0

class Poloniex(Service):
    service_id = 65
    api_homepage = "https://poloniex.com/support/api/"
    name = "Poloniex"
    exchange_fee_rate = 0.0025

    def __init__(self, api_key=None, api_secret=None, **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
        super(Poloniex, self).__init__(**kwargs)

    def check_error(self, response):
        j = response.json()
        if 'error' in j:
            raise ServiceError("Poloniex returned error: %s" % j['error'])

        super(Poloniex, self).check_error(response)

    def fix_symbol(self, symbol):
        if symbol.lower() == 'usd':
            return 'usdt'
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
            if fiat == 'usdt': fiat = 'usd'
            ret.append("%s-%s" % (crypto, fiat))
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

    def _trade_api(self, args):
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
        r = self._trade_api(params)
        return r.json()['orderNumber']
    make_order.supported_types = ['limit', 'fill-or-kill', 'post-only']
    make_order.minimums = {}

    def cancel_order(self, order_id):
        r = self._trade_api({
            "command": "cancelOrder",
            "orderNumber": order_id
        })
        return r['success'] == 1

    def list_orders(self, crypto=None, fiat=None):
        if not crypto and not fiat:
            pair = "all"
        else:
            self.make_market(crypto, fiat)

        resp = self._trade_api({
            "command": "returnOpenOrders",
            "currencyPair": pair,
        })
        return resp.json()

    def initiate_withdraw(self, crypto, amount, address):
        resp = self._trade_api({
            "command": "withdrawl",
            "currency": crypto,
            "amount": eight_decimal_places(amount),
            "address": address
        })
        return resp.json()

    def get_deposit_address(self, currency):
        c = self.fix_symbol(currency)
        resp = self._trade_api({"command": "returnDepositAddresses"})
        address = resp.json().get(c.upper())
        if not address:
            return self.generate_new_deposit_address(c)
        return address

    def generate_new_deposit_address(self, crypto):
        resp = self._trade_api({
            "command": "generateNewAddress",
            "currency": crypto.upper()
        })
        return resp.json()['response']

    def get_exchange_balance(self, currency, type="available"):
        if currency == 'usd':
            currency = 'usdt'
        resp = self._trade_api({
            "command": "returnBalances"
        })
        return float(resp.json().get(currency.upper()))

class Bittrex(Service):
    service_id = 66
    api_homepage = "https://bittrex.com/home/api"
    exchange_fee_rate = 0.0025

    def __init__(self, api_key=None, api_secret=None, **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
        super(Bittrex, self).__init__(**kwargs)

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

    def _trade_api(self, url, params):
        if not self.api_key or not self.api_secret:
            raise Exception("Trade API requires an API key and secret.")
        nonce = make_standard_nonce()
        params["apikey"] = self.api_key
        params["nonce"] = nonce
        url += "?" + urlencode(params)
        return self.get_url(url, headers={"apisign": self._make_signature(url)})

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        url = "https://bittrex.com/api/v1.1/market/%slimit" % side
        r = self._trade_api(url, {
            'market': self.make_market(crypto, fiat),
            'quantity': eight_decimal_places(amount),
            'rate': price
        })
        return r.json()['result']['uuid']
    make_order.supported_types = ['limit']
    make_order.minimums = {}

    def cancel_order(self, order_id):
        url = "https://bittrex.com/api/v1.1/market/cancel"
        r = self._trade_api(url, {'uuid': order_id})
        return r['success']

    def get_exchange_balance(self, currency, type="available"):
        if currency.lower() == 'usd':
            currency = 'usdt'
        url = "https://bittrex.com/api/v1.1/account/getbalance"
        resp = self._trade_api(url, {'currency': self.fix_symbol(currency)}).json()['result']
        return resp[type.capitalize()] or 0

    def get_deposit_address(self, crypto):
        url = "https://bittrex.com/api/v1.1/account/getdepositaddress"
        resp = self._trade_api(url, {'currency': self.fix_symbol(crypto)})
        return resp.json()['result']['Address']

    def initiate_withdraw(self, crypto, amount, address):
        url = "https://bittrex.com/api/v1.1/account/withdraw"
        resp = self._trade_api(url, {
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

    def get_current_price(self, crypto, fiat):
        url = "http://data.bter.com/api/1/ticker/%s_%s" % (crypto, fiat)
        response = self.get_url(url).json()
        if response.get('result', '') == 'false':
            raise ServiceError("BTER returned error: " + r['message'])
        return float(response['last'] or 0)

    def get_pairs(self):
        url = "http://data.bter.com/api/1/pairs"
        r = self.get_url(url).json()
        return [x.replace("_", "-") for x in r]

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

    def _trade_api(self, params):
        # max nonce wex will accept is 4294967294
        params['nonce'] = int(make_standard_nonce()) - 1505772471381
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
        return self._trade_api(params)
    make_order.supported_types = ['limit']
    make_order.minimums = {'btc': 0.001, 'ltc': 0.1}

    def get_deposit_address(self, crypto):
        params = {'coinName': crypto.lower(), 'method': 'CoinDepositAddress'}
        resp = self._trade_api(params).json()
        return resp['return']['address']

    def get_exchange_balance(self, currency, type="available"):
        resp = self._trade_api({'method': 'getInfo'}).json()
        try:
            return resp['return']['funds'][self.fix_symbol(currency).lower()]
        except IndexError:
            return 0


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


class HitBTC(Service):
    service_id = 109

    def get_pairs(self):
        url = 'https://api.hitbtc.com/api/1/public/symbols'
        r = self.get_url(url).json()['symbols']
        return [("%s-%s" % (x['commodity'], x['currency'])).lower() for x in r]

    def get_current_price(self, crypto, fiat):
        if crypto == 'bcc':
            raise SkipThisService("BCC not supported (maybe try BCH?)")
        if crypto == 'bch':
            crypto = 'bcc'

        pair = ("%s%s" % (crypto, fiat)).upper()
        url = "https://api.hitbtc.com/api/1/public/%s/ticker" % pair
        r = self.get_url(url).json()
        return float(r['last'])


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

    def _trade_api(self, params):
        params['nonce'] = make_standard_nonce(small=True)
        headers = {
            'Key':self.api_key,
            'Sign': self._make_signature(params)
        }
        return self.post_url('https://api.liqui.io', params, headers=headers)

    def get_exchange_balance(self, currency):
        resp = self._trade_api({'method': 'getInfo'}).json()
        return resp

    def list_orders(self, crypto=None, fiat=None):
        resp = self._trade_api({'method': 'ActiveOrders'}).json()
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

    def __init__(self, api_key=None, api_secret=None, **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
        super(Cryptopia, self).__init__(**kwargs)

    def check_error(self, response):
        r = response.json()
        error = r.get('Error', False)
        if error is not None:
            raise ServiceError("Cryptopia returned error: %s" % r['Error'])
        super(Cryptopia, self).check_error(response)

    def get_current_price(self, crypto, fiat):
        if fiat in ['nzd', 'usd']:
            fiat += "t"

        url = "https://www.cryptopia.co.nz/api/GetMarket/%s_%s" % (
            crypto.upper(), fiat.upper()
        )
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

    def _make_signature_header(self, url, params):

        nonce = str(int(time.time()*1000));
        b64 = base64.b64encode(hashlib.md5(json.dumps(params)).digest());
        signature = self.api_key + "POST" + url.lower() + nonce + b64;

        hmacsignature = base64.b64encode(hmac.new(base64.b64decode(self.api_secret), signature, hashlib.sha256).digest())
        parameter = self.api_key + ":" + hmacsignature + ":" + nonce;

        header_value = "amx " + parameter;
        return header_value


        strsecret = str(self.api_secret)
        strpublic = str(self.api_key)
        # Generate and grab the nonce
        tmpnonce = str(int(time.time() * 1000))
        # Set up MD5 object, encode params to bytes, MD5 hash
        md5params = hashlib.md5()
        encparams = json.dumps(params).encode("UTF-8")
        md5params.update(encparams)
        # Base64 the MD5 Hash & Return the bytes to a string, then assemble the request string
        b64request = base64.b64encode(md5params.digest())
        str64request = b64request.decode("UTF-8")
        reqstr = strpublic + "POST" + quote_plus(uri).lower() + tmpnonce + str64request
        # Sign the request string with the private key
        try:
            hmacraw = hmac.new(base64.b64decode(strsecret), reqstr.encode("UTF-8"), hashlib.sha256).digest()
        except:
            return "HMAC-SHA256 Signature failed! Check Private Key."
        # Base64 the signed parameters, assemble the header string and dict.
        hmacreq = base64.b64encode(hmacraw)
        return "amx " + strpublic + ":" + hmacreq.decode("UTF-8") + ":" + tmpnonce

    def _trade_api(self, url, args):
        return self.post_url(url, json=args, headers={
            "Authorization": self._make_signature_header(url, args),
            "Content-Type": "application/json; charset=utf-8"
        })

    def make_order(self, crypto, fiat, amount, price, type="limit", side="buy"):
        url = "https://www.cryptopia.co.nz/api/SubmitTrade"
        args = {
            'Market': ("%s/%s" % (crypto, fiat)).upper(),
            'Type': side,
            'Rate': price,
            'Amount': eight_decimal_places(amount)
        }
        resp = self._trade_api(url, args)
        return resp['Data']['OrderId']
    make_order.minimums = {}


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
