from __future__ import print_function

from moneywagon import ExchangeUniverse

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

def transfer_balance_on_exchange(currency, amount, from_ex, to_ex):
    to_address = to_ex.get_deposit_address(currency)
    return from_ex.initiate_withdraw(currency, amount, to_address)
