![Imgur](http://i.imgur.com/kLJqwqs.png)

moneywagon
==========

Python library for getting the current price of various cryptocurrencies.
This library is useful if you are building an application in Python that needs
to know the current price of any crypto-currency converted to any local fiat currency.

Installation
============

```
$ pip install moneywagon
```

High level API
==============

```python
>>> from moneywagon import get_current_price
>>> get_current_price('btc', 'usd')
(391.324, 'bitstamp')
>>> get_current_price('ltc', 'rur')
(169.54116322, 'cryptonator')
```

A two item tuple is always returned. The first item is the exchange rate (as a float), the second
item is a string describing the source for the exchange rate.

Optionally, be a good netizen and set a custom `User-Agent` string for
external requests, so API service maintainers know who is using their service:

```python
>>> get_current_price('btc', 'eur', useragent='My custom app 0.3b2')
(298.84381425, 'cryptonator')
```

If an external service is down, or the API has changed, or the
currency pairs is not implemented, an exception will be raised:

```python
>>> get_current_price('nxt', 'mex')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "moneywagon/__init__.py", line 22, in get_current_price
    raise Exception("Can not find price for %s to %s" % (crypto_symbol, fiat_symbol))
Exception: Can not find price for nxt to mex
```

Low level API
=============

The `get_current_price` function tries multiple services until it find one that returns a result.
If you would rather just use one service with no automatic retrying, use the low level 'getter' API:

```python
>>> from moneywagon.current_price import BTERPriceGetter
>>> getter = BTERPriceGetter("optional useragent string")
>>> getter.get_price('btc', 'usd')
(391.324, 'BTER')
```

Currently, this is a list of all supported getters:

```
CryptonatorPriceGetter, BTERPriceGetter, CoinSwapPriceGetter, BitstampPriceGetter, BTCEPriceGetter
```

Caching considerations
======================

The high level API does not do any caching of any sort. Each call to `get_current_price` will result in a
request with fresh results. On the other hand, the low level API will never make the request twice.

For instance, consider the following example:

```python
>>> from moneywagon.current_price import BTERPriceGetter
>>> getter = BTERPriceGetter()
>>> getter.get_price('ltc', 'rur') # makes two external calls, one for ltc->btc, one for btc->rur
(1.33535, 'bter')
>>> getter.get_price('btc', 'rur') # makes zero external calls (uses btc-> rur result from last call)
(1.33535, 'bter')
```

Note that the BTER exchange does not have a direct orderbook between litecoin and Russian ruble.
As a result, pycryptoprices needs to make two separate API calls to get the correct exchange rate.
The first one to get the LTC->BTC exchange rate, and the second one to get the BTC->RUR exchange rate.
Then the two results are multiplied together to get the LTC -> RUR exchange rate.
If your application does a lot of converting at a time, it will be better for performance to use
the low level API.

If you keep the original getter instance around and make more calls to get_price,
it will use the result of previous calls:

```python
>>> getter.get_price('btc', 'rur') # will make no external calls
(17865.4210346, 'cryptonator')
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

Donations
=========

If you would like to send a donation to support development, please send BTC here: 1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
