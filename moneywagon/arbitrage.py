from __future__ import print_function

from collections import defaultdict

from moneywagon import ExchangeUniverse
from moneywagon.services import Service

def all_balances(currency, services=None, verbose=False, timeout=None):
    """
    Get balances for passed in currency for all exchanges.
    """
    balances = {}
    if not services:
        services = [
            x(verbose=verbose, timeout=timeout)
            for x in ExchangeUniverse.get_authenticated_services()
        ]

    for e in services:
        try:
            balances[e] = e.get_exchange_balance(currency)
        except NotImplementedError:
            if verbose:
                print(e.name, "balance not implemented")
        except Exception as exc:
            if verbose:
                print(e.name, "failed:", exc.__class__.__name__, str(exc))

    return balances

def total_exchange_balances(services=None, verbose=None, timeout=None, by_service=False):
    """
    Returns all balances for all currencies for all exchanges
    """
    balances = defaultdict(lambda: 0)
    if not services:
        services = [
            x(verbose=verbose, timeout=timeout)
            for x in ExchangeUniverse.get_authenticated_services()
        ]

    for e in services:
        try:
            more_balances = e.get_total_exchange_balances()
            if by_service:
                balances[e.__class__] = more_balances
            else:
                for code, bal in more_balances.items():
                    balances[code] += bal
        except NotImplementedError:
            if verbose:
                print(e.name, "total balance not implemented")
        except Exception as exc:
            if verbose:
                print(e.name, "failed:", exc.__class__.__name__, str(exc))

    return balances

def transfer_balance_on_exchange(currency, from_ex, to_ex, percent=None, amount=None, verbose=False):
    if not isinstance(from_ex, Service): # if class passed in, instantiate
        from_ex = from_ex(verbose=verbose)
    if not isinstance(to_ex, Service):
        to_ex = to_ex(verbose=verbose)

    if not amount and not percent:
        raise Exception("One of `amount` or `percent` required.")
    if percent and amount:
        raise Exception("Either `amount` or `percent`, not both")

    if percent:
        balance = from_ex.get_exchange_balance(currency)
        amount = balance * (percent / 100)
        if verbose:
            print("Sending %.2f%% of %.8f which is %.8f" % (percent, balance, amount))
    to_address = to_ex.get_deposit_address(currency)
    if verbose:
        print("to address: %s" % to_address)
    return from_ex.initiate_withdraw(currency, amount, to_address)


class MultiOrderBook(object):

    def __init__(self, services=None, verbose=False):
        from moneywagon import EXCHANGE_SERVICES
        self.services = services or [x(verbose=verbose) for x in EXCHANGE_SERVICES]
        self.got_orderbook_services = []
        self.verbose = verbose

    def get(self, crypto, fiat, trim=False, trim_crypto=None, trim_fiat=None):
        services = None
        if trim:
            trim_crypto, trim_fiat = True, True
        if trim_fiat is True:
            trim_fiat = all_balances(fiat, services=self.services)
        if trim_crypto is True:
            if trim_fiat:
                services = trim_fiat.keys()
            else:
                services = self.services
            trim_crypto = all_balances(crypto, services=services)

        if trim_crypto or trim_fiat:
            services = self._services_from_balances(trim_crypto, trim_fiat)
        elif not services:
            services = self.services

        combined = {'bids': [], 'asks': []}
        for service in services:
            try:
                book = service.get_orderbook(crypto, fiat)
                combined = self._combine_orderbook(combined, book, service)
                self.got_orderbook_services.append(service)
            except NotImplementedError:
                pass
            except Exception as exc:
                print("%s orderbook failed: %s: %s" % (service.name, exc.__class__, str(exc)))

        if trim_fiat:
            combined['asks'] = self._trim(combined['asks'], trim_fiat, side='fiat')

        if trim_crypto:
            combined['bids'] = self._trim(combined['bids'], trim_crypto, side='crypto')

        return combined

    def _combine_orderbook(self, combined_book, new_book, new_book_service):
        for side in ['bids', 'asks']:
            for order in new_book[side]:
                with_name = (order[0], order[1], new_book_service)
                combined_book[side].append(with_name)

        combined_book['bids'] = sorted(combined_book['bids'], key=lambda x: x[0], reverse=True)
        combined_book['asks'] = sorted(combined_book['asks'], key=lambda x: x[0])

        return combined_book

    def _trim(self, book, balances, side):
        """
        >>> m = MultiOrderbook()
        >>> book = [
            [7800, 1.1, GDAX()],
            [7805, 3.2, Poloniex()],
            [7810, 0.3, GDAX()],
            [7900, 7.0, GDAX()]
        ]
        >>> m._trim(book, {GDAX(): 1.2, Poloniex(): 1.0}, 'crypto')
        [[7800, 1.1, <Service: GDAX (0 in cache)>],
         [7805, 1.0, <Service: Poloniex (0 in cache)>],
         [7810, 0.1, <Service: GDAX (0 in cache)>]]
        """
        new_book = []
        for service, balance in balances.items():
            accumulation = 0
            for order in book:
                if order[2].name == service.name:
                    if side == 'crypto':
                        size = order[1]
                    else:
                        size = order[1] * order[0] # convert to fiat

                    if size + accumulation <= balance:
                        new_book.append(order)
                        accumulation += size
                    else:
                        remaining = balance - accumulation
                        new_book.append([order[0], float("%.8f" % remaining), order[2]])
                        break

        return sorted(new_book, key=lambda x: x[0], reverse=side == 'fiat')

    def _services_from_balances(self, bal1, bal2):
        return (
            set(s for s,b in bal1.items() if b > 0) |
            set(s for s,b in bal2.items() if b > 0)
        )
