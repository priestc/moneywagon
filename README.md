pycryptoprices
==============

Python library for getting the current price of various cryptocurrencies.
This library is useful if you are building an application in Python that needs
to know the current price of any crypto-currency converted to any local fiat currency.

Installation
============

```
$ pip install pycryptoprices
```

High level API
==============

```python
>>> from pycryptoprices import get_current_price
>>> get_current_price('btc', 'usd')
(391.324, 'bitstamp')
>>> get_current_price('ltc', 'rur')
(3.486, 'bter (calculated)')
```

A two item tuple is always returned. The first item is the exchange rate (as a float), the second
item is a string describing the source for the exchange rate.

Optionally, be a good netizen and set a custom `User-Agent` string for
external requests, so API service maintainers know who is using their service:

```python
>>> get_current_price('btc', 'eur', useragent='My custom app 0.3b2')
(391.324, 'BTER (calculated)')
```

If an external service is down, or the API has changed, or the
currency pairs is not implemented, an exception will be raised:

```python
>>> get_current_price('nxt', 'mex')
[big ugly exception]
```

Low level API
=============

The `get_current_price` function tries multiple services until it find one that returns a result.
If you would rather just use one service with no automatic retrying, use the low level 'getter' API:

```python
>>> from pycryptoprices.getters import BTERPriceGetter
>>> getter = BTERPriceGetter("optional useragent string")
>>> getter.get_price('btc', 'usd')
(391.324, 'BTER')
```

Currently, this is a list of all supported getters:

```
CryptonatorPriceGetter, BTERPriceGetter, CoinSwapPriceGetter
```

Caching considerations
======================

The high level API does not do any caching of any sort. Each call to `get_current_price` will result in a
request with fresh results. On the other hand, the low level API will never make the request twice.

For instance, consider the following example:

```python
>>> from pycryptoprices.getters import BTERPriceGetter
>>> getter = BTERPriceGetter()
>>> getter.get_price('ltc', 'rur') # makes two external calls, one for ltc->btc, one for btc->rur
(1.33535, 'bter')
>>> getter.get_price('btc', 'rur') # makes zero external calls (uses btc-> rur result from last call)
(1.33535, 'bter')
```

Note that the BTER exchange does not have a direct orderbook between litecoin and Russian ruble. As a result, pycryptoprices
needs to make two separate API calls to get the correct exchange rate. The first one to get the litecoin -> BTC
exchange rate, and the second one to get the BTC -> RUR exchange rate. Then the two results are multiplied together
to get the LTC -> RUR exchange rate. If your application does a lot of converting at a time, it will be better
for performance to use the low level API.

If you keep the original getter instance around and make more calls to get_price, it will use the result of previous calls:

```python
>>> getter.get_price('btc', 'rur') # will make no external calls
(1.34563, 'bter')
```

In other words, if you are using the low level API and you want fresh values, you must make a new instance of the getter class.

Coming Soon
===========

* More backup data sources
* A way to fetch the exchange rate of a crypto/fiat currency at an arbitrary point in time. Using the HistoricalCryptoPrices service: https://github.com/priestc/HistoricalCryptoPrices


Contributing
============

If you would like to add a new service, feel free to make a pull request.
If you discover a service is no longer working feel free to create a github issue and some will fix it shortly.
