import datetime
import requests
import arrow

class HistoricalPriceGetter(object):
    pass

class QuandlHistoricalPriceGetter(HistoricalPriceGetter):
    def get_historical(fiat_symbol, crypto_symbol, date):
        """
        Using the quandl.com API, get the historical price (by day).
        All data comes from the CRYPTOCHART source, which claims to be from
        multiple exchange sources for price.
        """
        sources = [
            {'myr': ['CRYPTOCHART/MYR', datetime.timedelta(hours=36)]},
            {'doge': ['CRYPTOCHART/DOGE', datetime.timedelta(hours=36)]},
            {'ppc': ['CRYPTOCHART/PPC', datetime.timedelta(hours=36)]},
            {'ltc': ['BTCE/BTCLTC', datetime.timedelta(hours=36)]},
            {'vtc': ['CRYPTOCHART/VTC', datetime.timedelta(hours=36)]},
            {'nxt': ['CRYPTOCHART/NXT', datetime.timedelta(hours=36)]},
            {'ftc': ['CRYPTOCHART/FTC', datetime.timedelta(hours=36)]},
        ]

        source_list = sources[crypto_symbol.lower()]
        url = "https://www.quandl.com/api/v1/datasets/%s.json" % source_list[0]
        range = [date - source_list[0], date + source_list[0]]
        trim = "?trim_start={0:%Y-%m-%d}&trim_end={1:%Y-%m-%d}".format(range)

        return trim

        response = requests.get(url).json()
        for line in response['data']:
            tick_date = arrow.get(line[0]).datetime
            price = line[1]
            if price:
                price = float(price)

            p = PriceTick.objects.create(
                currency=currency,
                exchange=source.lower(),
                base_fiat='BTC',
                date=tick_date,
                price=price,
            )
            print p
