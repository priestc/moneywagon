from __future__ import print_function

from concurrent import futures
from moneywagon import get_address_balance, get_current_price
from moneywagon.core import NoService

def fetch_wallet_balances(wallets, fiat, **modes):
    """
    Wallets must be list of two item lists. First item is crypto, second item
    is the address. example:

    [
        ['btc', '1PZ3Ps9RvCmUW1s1rHE25FeR8vtKUrhEai'],
        ['ltc', 'Lb78JDGxMcih1gs3AirMeRW6jaG5V9hwFZ']
    ]
    """
    price_fetch = set([x[0] for x in wallets])
    balances = {}
    prices = {}

    fetch_length = len(wallets) + len(price_fetch)

    if not modes.get('async', False):
        # synchronous fetching
        for crypto in price_fetch:
            try:
                prices[crypto] = {'price': get_current_price(crypto, fiat, report_services=True, **modes)}
            except NoService as exc:
                prices[crypto] = {'error': str(exc)}

        for crypto, address in wallets:
            if address.replace('.', '').isdigit():
                balances[address] = {'balance': float(address)}
                continue

            try:
                balances[address] = {'balance': get_address_balance(crypto, address.strip(), **modes)}
            except NoService as exc:
                balances[address] = {'error': str(exc)}

    else:
        # asynchronous fetching
        if modes.get('verbose', False):
            print("Need to make", fetch_length, "external calls")

        with futures.ThreadPoolExecutor(max_workers=int(fetch_length / 2)) as executor:
            future_to_key = dict(
                (executor.submit(
                    get_current_price, crypto, fiat, report_services=True, **modes
                ), crypto) for crypto in price_fetch
            )

            future_to_key.update(dict(
                (executor.submit(
                    get_address_balance, crypto, address.strip(), **modes
                ), address) for crypto, address in wallets
            ))

            done, not_done = futures.wait(future_to_key, return_when=futures.ALL_COMPLETED)
            if len(not_done) > 0:
                print (not_done)
                import debug
                raise Exception("Broke") #not_done.pop().exception()

            for future in done:
                key = future_to_key[future]
                if len(key) > 5: # this will break if a crypto symbol is longer than 5 chars.
                    which = balances
                else:
                    which = prices

                res = future.result()
                which[key] = res

    ret = []

    for crypto, address in wallets:
        error = None
        if 'balance' in balances[address]:
            crypto_value = balances[address]['balance']
        else:
            crypto_value = 0
            error = balances[address]['error']

        if 'price' in prices[crypto]:
            sources, fiat_price = prices[crypto]['price']
        else:
            sources, fiat_price = [None], 0
            error = prices[crypto]['error']

        ret.append({
            'crypto': crypto,
            'address': address,
            'crypto_value': crypto_value,
            'fiat_value': (crypto_value or 0) * (fiat_price or 0),
            'conversion_price': fiat_price,
            'price_source': sources[0].name,
            'error': error
        })

    return ret
