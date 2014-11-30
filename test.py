from __future__ import print_function

import datetime

from moneywagon import CurrentPrice, HistoricalPrice, AddressBalance, HistoricalTransactions

current_price = CurrentPrice()
historical_price = HistoricalPrice()
address_balance = AddressBalance(verbose=True)
historical_transactions = HistoricalTransactions()

while_ago = datetime.datetime.now() - datetime.timedelta(days=7)


for fiat in ['usd', 'gbp', 'eur', 'jpy', 'cny', 'cad', 'rur', 'btc']:
    for crypto in ['btc', 'ltc', 'myr', 'ppc', 'vtc', 'rdd', 'drk', 'ftc', 'cinni']:
        pair = '%s-%s' % (crypto, fiat)
        #print(pair, "Current Price:", current_price.get_price(crypto, fiat))
        #print(pair, "Historical Price:", historical_price.get_historical(crypto, fiat, while_ago))


wallets = [
    ['btc', '1JhtQAGKApRgxWvRASGAH8qggtVNQMU47d'],
    ['ltc', 'Lb78JDGxMcih1gs3AirMeRW6jaG5V9hwFZ'],
    ['ppc', 'PVoei4A3TozCSK8W9VvS55fABdTZ1BCwfj'],
    ['doge', 'D8ZXs3JDdLuyRjG3wDtRQE2PMT4YQWELfZ'],
    ['rdd', 'RbHsU84Eo5tUBj7HDNEb9ZSw2fFhU1NKgD'],
    ['drk', 'XrbZsLp9QDSf8usYYMPhmKWA8u1kQ26rQJ'],

    ['vtc', 'Va3LcDhwrcwGtG366jeP6EJzWnKT4yMDxs'],
    ['nxt', 'NXT-ZMUQ-729K-5AM6-4AAYM'],
    ['myr', 'MHEipvGqerT3XDp2hq62xtnCujS4qL67DZ'],
    #['ftc', '6tE27DEB6HgnofAFPFtCyQ9aDaCD828YRq'],


]

for crypto, address in wallets:
    print("Balance:", crypto, address_balance.get_balance(crypto, address))
    print("Trans:", historical_transactions.get_transactions(crypto, address))
