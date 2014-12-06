from .service import Service, SkipThisService, AutoFallback

class OldCryptoCoinChartsCurrentPrice(Service):
    """
    Using raw rest API (looks to be currently broken)
    """
    def get_price(self, crypto, fiat):
        url = "http://api.cryptocoincharts.info/tradingPairs/%s_%s" % (
            crypto, fiat
        )
        response = self.get_url(url).json()
        return float(response['price'] or 0), response['best_market']


class CryptoCoinChartsCurrentPrice(Service):
    """
    Using fancy API client library (currently broken)
    """
    def get_price(self, crypto, fiat):
        from CryptoCoinChartsApi import API as CCCAPI
        api = CCCAPI()
        tradingpair = api.tradingpair("%s_%s" % (crypto, fiat))
        return tradingpair.price, tradingpair.best_market
