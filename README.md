![Imgur](http://i.imgur.com/kLJqwqs.png)

moneywagon
==========

Python library containing various tools relating to cryptocurrencies.
This tool is still being developed, but currently has two principle functions:

1. Getting the **current** exchange rate of any cryptocurrency (LTC, BTC, PPC, etc) and a
fiat currency (USD, EUR, RUR, etc.)
2. Getting the exchange rate between a cryptocurrency and a fiat currency **at an
arbitrary point in time**.

There is a third planned part of moneywagon that has not yet been buily.
This section will be a fancy API for creating transactions.

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
>>> from moneywagon.current_price import CurrentPrice, BTERCurrentPrice
>>> getter = BTERCurrentPrice()
>>> getter.get_price('btc', 'usd')
(391.324, 'BTER')
```

If you use the `CryptoPrice` class, the get_price method will try all getters
until a value is returned (same as high level API). If you use a getter class
that is limited to one API service, such as "BTERCurrentPrice",
then only that service will be called.

Here is a list of all supported getters for purrent price:

class name                  | API
----------------------------|--------------
| `CryptonatorCurrentPrice` | https://www.cryptonator.com/api
| `BTERCurrentPrice`        | https://bter.com/api
| `CoinSwapCurrentPrice`    | https://coin-swap.net/api
| `BitstampCurrentPrice`    | https://www.bitstamp.net/api/
| `BTCECurrentPrice`        | https://btc-e.com/api/documentation

Caching considerations
----------------------

The high level API does not do any caching of any sort. Each call to `get_current_price` will result in a
request with fresh results. On the other hand, the low level API will never make the request twice.

For instance, consider the following example:

```python
>>> from moneywagon.current_price import BTERCurrentPrice
>>> getter = BTERCurrentPrice()
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

When using the high-level price API (or the `CurrentPrice` class), if the highest order
API service is not able to return a response, the next API will be called instead.
The order of API service precidence is:

1. Bitstamp (BTC->USD only)
2. BTC-e
3. Cryptonator
4. BTER
5. Coinswap

The result is that almost every single fiat/crypto is guaranteed to return a result
even if one or more API services are down.

On the other hand, if you call one of the API specific getter classes (such as `CoinSwapCurrentPrice`)
no fallback calls will occur. If the CoinSwap API does not support the passed in crypto/fiat pair,
or if the service is not running, the call will raise an exception.

Historical Cryptocurrency Price
===============================

The API is similar to the low-level current price API.
There are two differences:

1. The method is named `get_historical` instead of `get_price`.
2. It takes an extra argument `at_time`. This can be a either a `datetime` instance
representing when you'd like to get the price, or a string that will get converted to a
datetime object by arrow.get..

```python
>>> from datetime import datetime
>>> from moneywagon import HistoricalCryptoPrice
>>> getter = HistoricalCryptoPrice(useragent="my app")
>>> getter.get_historical('btc', 'usd', '2013-11-13')
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
>>> getter.get_historical('vtc', 'rur', '2014-11-13'))
(3.2636992,
'CRYPTOCHART/VTC x BITCOIN/BTCERUR',
datetime.datetime(2014, 11, 13, 0, 0))
```

In this case, moneywagon first gets the conversion rate from VTC-BTC on 2014-11-13.
Then it gets hte conversion rate for BTC->RUR on 2014-11-13.
The result that is returned is those two values multiplied together.
This is similar to the process described earlier
The nature of this calculation can also be seen in the source string
(the second item in the response).

Transaction API
===============

The transaction API has been designed to be as simple and easy to use as possible.
No knowledge of cryptography is needed. You do need to know the basics of how
cryptocurrency transactions work.

Just like the price getter API's, the transaction API available via a
"Low Level API" and a "High Level API"

High Level API
--------------

```python
from moneywagon import Transaction

t = Transaction(
    crypto='btc'
    to='1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X',
    from='1DBQgauyuSodrPctQojRtAUfHncU1ECghW',
    private_key='5KBudDby7NFod41Jkbb8s9KgiFi6GuTvnMBsiNZkgFV2c3Bijvv'
    amount=0.023,
    fee=0.00001,
)

t.verify() # checks if the
t.send()
```

Low Level API
-------------

```python
from moneywagon.transactions import get_unspent_outputs, make_transaction, send_transaction
outputs = get_unspent_outputs('btc', '1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X')
raw_transaction = make_transaction(
    outputs=outputs,
    amount=0.0023,
    to='1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X',
    private_key='5KBudDby7NFod41Jkbb8s9KgiFi6GuTvnMBsiNZkgFV2c3Bijvv'
)
send_transaction('btc', raw_transaction)
```


Contributing
============

If you would like to add a new service, feel free to make a pull request.
If you discover a service is no longer working feel free to create a github issue and some will fix it shortly.

Donations
=========

If you would like to send a donation to support development, please send BTC here: 1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
