import datetime
import requests
import arrow
import pytz

from current_price import PriceGetter

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

class QuandlHistoricalPriceGetter(PriceGetter):
    def get_historical(self, crypto, fiat, at_time):
        """
        Using the quandl.com API, get the historical price (by day).
        The CRYPTOCHART source claims to be from multiple exchange sources
        for price (they say best exchange is most volume).
        """
        # represents the 'width' of the quandl data returned (one day)
        # if quandl ever supports data hourly or something, this can be changed
        interval = datetime.timedelta(hours=24)
        crypto = crypto.lower()
        fiat = fiat.lower()

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
            sources = {
                'myr': ['CRYPTOCHART/MYR', 1],
                'doge': ['CRYPTOCHART/DOGE', 1],
                'ppc': ['CRYPTOCHART/PPC', 1],
                'ltc': ['BTCE/BTCLTC', 4],
                'vtc': ['CRYPTOCHART/VTC', 1],
                'nxt': ['CRYPTOCHART/NXT', 1],
                'ftc': ['CRYPTOCHART/FTC', 1],
            }
            source, price_index = sources[crypto.lower()]

        url = "https://www.quandl.com/api/v1/datasets/%s.json" % source
        trim = "?trim_start={0:%Y-%m-%d}&trim_end={1:%Y-%m-%d}".format(
            at_time - interval, at_time + interval
        )

        response = self.fetch_url(url + trim).json()
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
            msg = "Data source is incomplete. Could not get best price for %s/%s on %s." % (
                crypto, fiat, at_time
            )
            raise Exception(msg)

        return best_price, source, best_date
