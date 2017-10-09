from moneywagon import ExchangeUniverse

def all_balances(currency, services=None, verbose=False, timeout=None):
    """
    Get balances for passed in currency for all exchanges.
    """
    balances = {}
    for Exchange in (services or ExchangeUniverse.get_authenticated_services()):
        try:
            balances[Exchange.name] = Exchange(verbose=verbose, timeout=timeout).get_exchange_balance(currency)
        except NotImplementedError:
            pass
        except Exception as exc:
            print(Exchange.name, "failed:", str(exc))

    return balances

def transfer_balance_on_exchange(currency, amount, from_ex, to_ex):
    to_address = to_ex.get_deposit_address(currency)
    return from_ex.initiate_withdraw(currency, amount, to_address)
