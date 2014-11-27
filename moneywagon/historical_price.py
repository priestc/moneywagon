import datetime
import requests
import arrow
import pytz

from current_price import PriceGetter

class QuandlHistoricalPriceGetter(PriceGetter):
    def get_historical(self, fiat_symbol, crypto_symbol, at_time):
        """
        Using the quandl.com API, get the historical price (by day).
        All data comes from the CRYPTOCHART source, which claims to be from
        multiple exchange sources for price.
        """
        if fiat_symbol.lower() != 'btc':
            raise Exception("Only BTC base price supported for now")

        sources = {
            'myr': ['CRYPTOCHART/MYR', datetime.timedelta(hours=36), 1],
            'doge': ['CRYPTOCHART/DOGE', datetime.timedelta(hours=36), 1],
            'ppc': ['CRYPTOCHART/PPC', datetime.timedelta(hours=36), 1],
            'ltc': ['BTCE/BTCLTC', datetime.timedelta(hours=36), 4],
            'vtc': ['CRYPTOCHART/VTC', datetime.timedelta(hours=36), 1],
            'nxt': ['CRYPTOCHART/NXT', datetime.timedelta(hours=36), 1],
            'ftc': ['CRYPTOCHART/FTC', datetime.timedelta(hours=36), 1],
        }

        source, interval, price_index = sources[crypto_symbol.lower()]
        url = "https://www.quandl.com/api/v1/datasets/%s.json" % source
        trim = "?trim_start={0:%Y-%m-%d}&trim_end={1:%Y-%m-%d}".format(
            at_time - interval, at_time + interval
        )

        response = self.fetch_url(url + trim).json()
        closest_distance = interval

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

        return best_price, source, best_date
