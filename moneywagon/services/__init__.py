from .blockchain_services import *
from .exchange_services import *

def get_service(name=None, id=None):
    from moneywagon import ALL_SERVICES
    for service in ALL_SERVICES:
        if (name and service.name.lower() == name.lower()) or (id and service.id == id):
            return service

def _get_all_services(crypto=None, just_exchange=False):
    """
    Go through the crypto_data structure and return all list of all (unique)
    installed services. Optionally filter by crypto-currency.
    """
    from moneywagon.crypto_data import crypto_data

    if not crypto:
        # no currency specified, get all services
        to_iterate = crypto_data.items()
    else:
        # limit to one currency
        to_iterate = [(crypto, crypto_data[crypto])]

    services = []
    for currency, data in to_iterate:
        if 'services' not in data:
            continue
        if currency == '':
            continue # template

        # price services are defined as dictionaries, all other services
        # are defined as a list.
        price_services = data['services']['current_price']
        del data['services']['current_price']

        all_services = list(price_services.values())
        if not just_exchange:
            all_services += list(data['services'].values())

        # replace
        data['services']['current_price'] = price_services

        services.append([
            item for sublist in all_services for item in sublist
        ])

    return sorted(
        set([item for sublist in services for item in sublist]),
        key=lambda x: x.__name__
    )

class BadService(Service):
    service_id = 0

    def get_balance(self, crypto, address, confirmations=1):
        class FakeResponse(object):
            def json(self):
                return {}
        self.last_raw_response = FakeResponse()
        return 999999
