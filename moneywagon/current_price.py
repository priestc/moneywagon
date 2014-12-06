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










class CurrentPrice(AutoFallback):
    service_classes = [
        BitstampCurrentPrice,
        BTCECurrentPrice,
        CryptonatorCurrentPrice,
        BTERCurrentPrice,
        CoinSwapCurrentPrice
    ]
    method_name = 'get_price'

    def get_price(self, crypto, fiat):
        crypto = crypto.lower()
        fiat = fiat.lower()

        if crypto == fiat:
            return (1.0, 'math')

        return self._try_each_service(crypto, fiat)

    def no_service_msg(self, crypto, fiat):
        return "Can not find price for %s->%s" % (crypto, fiat)
