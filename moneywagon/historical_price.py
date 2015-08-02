from __future__ import print_function

import datetime
import requests
import arrow
import pytz

from .core import Service, NoData
from .crypto_data import crypto_data

quandl_exchange_btc_to_fiat = {
    'ARS': 'localbtc',
    'AUD': 'weex',
    'BRL': 'bbm',
    'CAD': 'virtex',
    'CHF': 'localbtc',
    'CLP': 'th',
    'CNY': 'anxhk',
    'CZK': 'bitcash',
    'DKK': 'localbtc',
    'EUR': 'btce',
    'GAU': 'bcmBM',
    'GBP': 'britcoin',
    'HKD': 'anxhk',
    'HUF': 'ruxum',
    'ILS': 'bit2c',
    'INR': 'localbtc',
    'JPY': 'btcex',
    'MXN': 'localbtc',
    'NOK': 'just',
    'NZD': 'bitnz',
    'PLN': 'bitcurex',
    'RUB': 'ruxum',
    'RUR': 'btce',
    'SEK': 'ruxum',
    'SGD': 'ruxum',
    'SLL': 'virwox',
    'THB': 'ruxum',
    'UAH': 'ruxum',
    'WMR': 'btcex',
    'WMZ': 'btcex',
    'XRP': 'ripple',
    'YAD': 'btcex',
    'ZAR': 'bitx',
}

class Quandl(Service):
    def get_historical_price(self, crypto, fiat, at_time):
        """
        Using the quandl.com API, get the historical price (by day).
        The CRYPTOCHART source claims to be from multiple exchange sources
        for price (they say best exchange is most volume).
        """
        # represents the 'width' of the quandl data returned (one day)
        # if quandl ever supports data hourly or something, this can be changed
        interval = datetime.timedelta(hours=48)
        crypto = crypto.lower()
        fiat = fiat.lower()

        at_time = arrow.get(at_time).datetime

        data = crypto_data[crypto]
        name, date_created = data['name'], data['genesis_date']

        if date_created.replace(tzinfo=pytz.utc) > at_time:
            raise Exception("%s (%s) did not exist on %s" % (name, crypto, at_time))

        if crypto == 'btc':
            # Bitcoin to fiat
            if fiat == 'usd':
                if at_time < datetime.datetime(2013, 2, 1, tzinfo=pytz.utc):
                    exchange = 'MtGox'
                else:
                    exchange = "Bitstamp"
            else:
                exchange = quandl_exchange_btc_to_fiat[fiat.upper()]

            source = "BITCOIN/%s%s" % (exchange.upper(), fiat.upper())
            price_index = 1
        else:
            # some altcoin to bitcoin
            if fiat != 'btc':
                raise Exception("Altcoins are only available via BTC base fiat")
            if crypto == 'ltc':
                source, price_index = ['BTCE/BTCLTC', 4]
            else:
                source, price_index = ['CRYPTOCHART/' + crypto.upper(), 1]

        url = "https://www.quandl.com/api/v1/datasets/%s.json" % source
        trim = "?trim_start={0:%Y-%m-%d}&trim_end={1:%Y-%m-%d}".format(
            at_time - interval, at_time + interval
        )

        response = self.get_url(url + trim).json()
        closest_distance = interval

        best_price = None
        for line in response['data']:
            date = line[0]
            price = line[price_index]
            tick_date = arrow.get(date).datetime
            distance = at_time - tick_date

            if distance.total_seconds() == 0:
                return price, source, tick_date

            if distance < closest_distance:
                closest_distance = distance
                best_price = price
                best_date = tick_date

        if not best_price:
            msg = "Quandl's data source is incomplete. Could not get best price for %s/%s on %s." % (
                crypto, fiat, at_time
            )
            raise NoData(msg)

        return best_price, source, best_date
