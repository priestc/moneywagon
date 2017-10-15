from __future__ import print_function

from moneywagon import ExchangeUniverse

def all_balances(currency, services=None, verbose=False, timeout=None, benchmark=False):
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
        e.benchmark = benchmark
        try:
            balances[e] = e.get_exchange_balance(currency)
        except NotImplementedError:
            pass
        except Exception as exc:
            print(e.name, "failed:", str(exc))

    return balances

def transfer_balance_on_exchange(currency, amount, from_ex, to_ex):
    to_address = to_ex.get_deposit_address(currency)
    return from_ex.initiate_withdraw(currency, amount, to_address)
