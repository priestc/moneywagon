from moneywagon.core import Service
from moneywagon.crypto_data import crypto_data

class ShapeShiftIO(Service):

    api_homepage = "https://info.shapeshift.io/"

    def onchain_exchange_rates(self):
        pairs = self.get_url("https://shapeshift.io/marketinfo/").json()
        final_pairs = []

        for pair in pairs:
            deposit_code, withdraw_code = pair['pair'].split("_")
            try:
                deposit_name = crypto_data[deposit_code.lower()]['name']
            except (KeyError, TypeError): # currency not supported by moneywagon
                continue

            try:
                withdraw_name = crypto_data[withdraw_code.lower()]['name']
            except (KeyError, TypeError): # currency not supported by moneywagon
                continue

            final_pairs.append({
                'deposit_currency': {'code': deposit_code, 'name': deposit_name},
                'withdraw_currency': {'code': withdraw_code, 'name': withdraw_name},
                'rate': pair['rate'],
                'max_amount': pair['maxLimit'],
                'min_amount': pair['min'],
                'withdraw_fee': pair['minerFee'],
                'service': self
            })

        return final_pairs

    def onchain_exchange_status(self, deposit_address):
        return self.get_url("https://shapeshift.io/txStat/" + deposit_address).json()

    def get_onchain_exchange_address(self, deposit_crypto, withdraw_crypto, withdraw_address):
        url = "https://shapeshift.io/shift"
        pair = (deposit_crypto + "_" + withdraw_crypto).lower()
        return self.post_url(url, {'withdrawal': withdraw_address, 'pair': pair}).json()


# class MultiExplorerExchange(Service):
#
#     def onchain_exchange_rates(self):
#         return [
#         {
#         'deposit_currency': {'code': u'LTC', 'name': 'Litecoin'},
#         'max_amount': 508.36657379,
#         'min_amount': 0.09404389,
#         'rate': u'0.07631284',
#         'service': self,
#         'withdraw_currency': {'code': u'BTC', 'name': 'Bitcoin'},
#         'withdraw_fee': 0.0003}
#      ]


ALL_SERVICES = [ShapeShiftIO]
