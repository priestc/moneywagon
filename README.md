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

Current Price
=============

High level API
--------------

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
    raise Exception("Can not find price for %s to %s" % (crypto, fiat))
Exception: Can not find price for nxt to mex
```

Low level API
-------------

The `get_current_price` function tries multiple services until it find one that returns a result.
If you would rather just use one service with no automatic retrying, use the low level 'getter' API:

```python
>>> from moneywagon.current_price import BTERPriceGetter
>>> getter = BTERPriceGetter("optional useragent string")
>>> getter.get_price('btc', 'usd')
(391.324, 'BTER')
```

Currently, this is a list of all supported getters:


class name                 | API
---------------------------|--------------
| `CryptonatorPriceGetter` | https://www.cryptonator.com/api
| `BTERPriceGetter`        | https://bter.com/api
| `CoinSwapPriceGetter`    | https://coin-swap.net/api
| `BitstampPriceGetter`    | https://www.bitstamp.net/api/
| `BTCEPriceGetter`        | https://btc-e.com/api/documentation

Caching considerations
----------------------

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

Automatic API fallback
----------------------

When using the high-level price API (or the `CurrentCryptoPrice` class), if the highest order
API service is not able to return a response, the next API will be called instead.
The order of API service precidence is:

1. Bitstamp (BTC->USD only)
2. BTC-e
3. Cryptonator
4. BTER
5. Coinswap

The result is that almost every single fiat/crypto is guaranteed to return a result
even if one or more API services are down.

On the other hand, if you call one of the API specific getter classes (such as `CoinSwapPriceGetter`)
no fallback calls will occur. If the CoinSwap API does not support the passed in crypto/fiat pair,
or if the service is not running, the call will raise an exception.

Historical Cryptocurrency Price
===============================

The API is similar to the low-level current price API.
There are two differences:

1. The method is named `get_historical` instead of `get_price`.
2. It takes an extra argument `at_time`. This should be a `datetime` instance
representing when you'd like to get the price.

```python
>>> from datetime import datetime
>>> from moneywagon import HistoricalCryptoPrice
>>> getter = HistoricalCryptoPrice(useragent="my app")
>>> getter.get_historical('btc', 'usd', datetime(2013, 11, 13))
(354.94,
'BITCOIN/BITSTAMPUSD',
datetime.datetime(2013, 11, 13, 0, 0))
```

The result is the same, except there is a third item in the tuple.
This third value is the time of the actual price.
There are gaps in Quandl's data, so sometimes the actual price returned
is from a day before or a day after.

Unlike the current price API, the historical price API only has an implementation for one service,
and that service is Quandl.com. If Quandl is ever down, this feature will not work.
If you know of an API service that hosts historical cryptocurrency prices,
please let the moneywagon developers know.

Also, the Quandl service does not have every single cryptocurrency to fiat exchange history,
so for some pairs, moneywagon has to make two different calls to Quandl.

```python
>>> getter.get_historical('vtc', 'rur', datetime(2014, 11, 13))
(3.2636992,
'CRYPTOCHART/VTC x BITCOIN/BTCERUR',
datetime.datetime(2014, 11, 13, 0, 0))
```

In this case, moneywagon first gets the conversion rate from VTC-BTC on 2014-11-13.
Then it gets hte conversion rate for BTC->RUR on 2014-11-13.
The result that is returned is those two values multiplied together.
The nature of this calculation can also be seen in the source string
(the second item in the response).


Coming Soon
===========

* More backup data sources
* Super easy API for creating a transaction for any cryptocurrency


Contributing
============

If you would like to add a new service, feel free to make a pull request.
If you discover a service is no longer working feel free to create a github issue and some will fix it shortly.

Donations
=========

If you would like to send a donation to support development, please send BTC here: 1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
