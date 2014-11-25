pycryptoprices
==============

Python library for getting the current price of various cryptocurrencies.
This library is useful if you are building an application in Python that needs
to know the current price of any crypto-currency.

Installation
============

    $ pip install pycryptoprices

Basic Usage
===========

    >>> from pycryptoprices import get_current_price
    >>> get_current_price('btc', 'usd')
    (391.324, 'bitstamp')
    >>> get_current_price('ltc', 'rur')
    (391.324, 'BTER (calculated)')

    A two item tuple is always returned. The first item is the exchange  rate (as a float), the second
    item is a string describing the source for the exchange rate.

    Optionally, be a good netizen and set a custom useragent string for
    external requests, so API service maintainers know who is using their service:

    >>> get_current_price(‘btc’, ‘eur’, useragent=My custom app 0.3b2’)
    (391.324, 'BTER (calculated)')

    If an external service is down, or the API has changed, or the
    currency pairs is not implemented, an exception will be raised:

    >>> get_current_price('ltc', 'mex')
    [big ugly exception]

Getting from a single service
=============================

The `get_current_price` function tries multiple services until it find one that returns a result.
If you would rather just use one service with no automatic retrying, use the following API:

    >>> from pycryptoprices.getters import BTERPriceGetter
    >>> getter = BTERPriceGetter(“optional useragent string”)
    >>> getter.get_price(‘btc’, usd’)
    (391.324, 'BTER')

Contributing
============

If you would like to add a new service, feel free to make a pull request.
If you discover a service is no longer working