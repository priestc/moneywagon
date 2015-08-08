![Imgur](http://i.imgur.com/kLJqwqs.png)

# moneywagon


Moneywagon lets you build a bitcoin wallet application in Python without
ever having to rely on a single blockchain API service. This library is Python 2
and Python 3 compatible.

For instance, lets say you are building an application in Python that
needs to know the current exchange rate between BTC and USD. Before moneywagon,
you had to hardcode your application to make an HTTP request to a single service like
bitstamp to get the current price. If the bitstamp API were ever to change, your
code would break, wasting development time. With moneywagon, you code your application
to the moneywagon API (which doesn't change), and under the hood you can swap between services.

This tool is still being developed, but currently has 5 principle functions:

1. Getting the **current** exchange rate of any cryptocurrency (LTC, BTC, PPC, etc) and a
fiat currency (USD, EUR, RUR, etc.)
2. Getting the exchange rate between a cryptocurrency and a fiat currency **at an
arbitrary point in time**.
3. Getting the balance of an address for any cryptocurrency.
4. Getting a list of historical transaction from an address for any cryptocurrency.
5. A Bitcore-esque wrapper class for making transactions (BTC only for now).
6. Command line interface for accessing all of moneywagon's functionality from the shell.

There is a sixth planned part of moneywagon that has not yet been built.
This section will be a fancy API for creating transactions.

# Installation

```
$ pip install moneywagon
```

# Command Line Interface

There are currently 6 functions available through the command line interface:

## current-price [crypto] [fiat]

This gets the current exchange rate between any cryptocurrency and any fiat currency.

examples:

```
$ moneywagon current-price ltc eur
3.798
```

Additionally, you can include `--verbose` to get more output:

```
$ moneywagon current-price btc usd --verbose
* Trying: <Service: Bitstamp (0 in cache)>
URL: https://www.bitstamp.net/api/ticker/
279.01

```

## address-balance [crypto] [address]

Gets the amount of currency currently assiciated with a cryptocurrency address.

examples:

```
moneywagon address-balance doge D8ZXs3JDdLuyRjG3wDtRQE2PMT4YQWELfZ
99405.6048377
```

Also you can include a `--verbose` flag to get more onput:

```
$ moneywagon address-balance vtc Va3LcDhwrcwGtG366jeP6EJzWnKT4yMDxs --verbose
* Trying: <Service: ThisIsVTC (0 in cache)>
URL: http://explorer.thisisvtc.com/api/addr/Va3LcDhwrcwGtG366jeP6EJzWnKT4yMDxs/balance
99.5
```

An additional parameter, `--paranoid=n` can be added to crosscheck multiple services.
The number `n` corresponds to how many services to check:

```
$ moneywagon address-balance btc 1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X --paranoid=5 --verbose
* Trying: <Service: Toshi (0 in cache)>
URL: https://bitcoin.toshi.io/api/v0/addresses/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
* Trying: <Service: BlockCypher (0 in cache)>
URL: http://api.blockcypher.com/v1/btc/main/addrs/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
* Trying: <Service: Blockr (0 in cache)>
URL: http://btc.blockr.io/api/v1/address/info/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
* Trying: <Service: BlockStrap (0 in cache)>
URL: http://api.blockstrap.com/v0/btc/address/id/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
* Trying: <Service: ChainSo (0 in cache)>
URL: https://chain.so/api/v2/get_address_balance/btc/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X/1
0.00132132
```

## moneywagon historical-transactions [crypto] [address]

Gets a list of all transactions sent and received by the passed in cryptocurrency address.
The resulting output is always valid json. The most recent transaction is always at the top.

```
$ moneywagon historical-transactions doge D8ZXs3JDdLuyRjG3wDtRQE2PMT4YQWELfZ | python -m json.tool
[
    {
        "amount": 66.72788462,
        "confirmations": 248634,
        "date": "2015-02-07T18:04:05+00:00",
        "txid": "a7cfe62ad255cb1e77762ab196455eae974fb9010023f60761fc8a25b1a9f8ec"
    },
    {
        "amount": 67.96625,
        "confirmations": 256753,
        "date": "2015-02-01T19:36:39+00:00",
        "txid": "fb371d55ce172ee015e110fa7896c8920af64aa3befe01b2596b99bbff35e5f7"
    },
    {
        "amount": 68.02740385,
        "confirmations": 256753,
        "date": "2015-02-01T19:36:39+00:00",
        "txid": "a04454ed38f9a587cc6c6d4730758fe38c60aca8153f2b0890b9163baf343f49"
    },
    {
        "amount": 68.01211538,
        "confirmations": 256753,
        "date": "2015-02-01T19:36:39+00:00",
        "txid": "7999040a76978d32c7dae5acbbccd1e899027595dba172b7458d9763b0cb3855"
    },
    {
        "amount": 69.17061567,
        "confirmations": 274609,
        "date": "2015-01-19T18:39:16+00:00",
        "txid": "ecd6a0c21873d307639be35d029347583a645d0ce0a924e75524b26b27904dd1"
    },
    {
        "amount": 70.70056818,
        "confirmations": 275074,
        "date": "2015-01-19T10:30:05+00:00",
        "txid": "3fe38e89f25c9fb424970ae8c763064adaa15af357ecf49602f73e5912845f27"
    },
    {
        "amount": 98995.0,
        "confirmations": 561926,
        "date": "2014-06-15T23:48:44+00:00",
        "txid": "b6bd31a9d4db7a6d54a64086a0a51432336fb18338bece3f8382faa79728fbfc"
    }
]
```

This command also supports the `--verbose` and `--paranoid=n` flags (see above).

## moneywagon wallet-balance [wallet path] [fiat]

Get the fiat total of a group of cryptocurrency addresses from a "csv wallet" file.

example:

```
$ cat ~/wallets.csv
doge,D8ZXs3JDdLuyRjG3wDtRQE2PMT4YQWELfZ
btc,1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
$ moneywagon wallet-balance ~/wallets.csv usd
```


# Python Interface


## Current Price


```python
>>> from moneywagon import get_current_price
>>> get_current_price('btc', 'usd')
(391.324, 'bitstamp')
>>> get_current_price('ltc', 'rur')
(169.54116322, 'cryptonator')
```

A two item tuple is always returned. The first item is the exchange rate (as a float), the second
item is a string describing the source for the exchange rate.

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

## Historical Cryptocurrency Price


The API is similar to the low-level current price API.
There are two differences:

1. The method is named `get_historical` instead of `get_price`.
2. It takes an extra argument `at_time`. This can be a either a `datetime` instance
representing when you'd like to get the price, or a string that will get converted to a
datetime object by arrow.get..

```python
>>> from datetime import datetime
>>> from moneywagon import HistoricalCryptoPrice
>>> service = HistoricalCryptoPrice(useragent="my app")
>>> service.get('btc', 'usd', '2013-11-13')
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
>>> service.get('vtc', 'rur', '2014-11-13'))
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

## Address Balance

```python
>>> from moneywagon import AddressBalance
>>> AddressBalance().get('ppc', 'PVoei4A3TozCSK8W9VvS55fABdTZ1BCwfj')
103.98
```

## Historical Transactions


```python
>>> from moneywagon import HistoricalTransactions
>>> HistoricalTransactions().get('ltc', 'Lb78JDGxMcih1gs3AirMeRW6jaG5V9hwFZ')
[{'amount': 147.58363366,
'confirmations': 9093,
'date': datetime.datetime(2014, 11, 16, 23, 53, 37, tzinfo=tzutc()),
'txid': u'cb317dec84514773f34e4258cd0ff49eed6bfcf1770709b1ed07855d2e1a4aa4'},
{'amount': 19.7,
'confirmations': 100494,
'date': datetime.datetime(2014, 6, 16, 0, 7, 26, tzinfo=tzutc()),
'txid': u'846d316f369906f990262e1758eb0a2a953ebd47a9b1cf13d57aadc9ad2e19a3'},
{'amount': 71.75600005,
'confirmations': 219032,
'date': datetime.datetime(2013, 11, 27, 16, 36, 14, tzinfo=tzutc()),
'txid': u'9152784755564c3c680aa47a3a1cdc28e4896657bfc2e60626a0ee22b200af7c'}]
```

## Creating Transactions


There is a wrapper class that helps you make transactions. Here is how to use it:

```python
>>> from moneywagon.tx import Transaction
>>> tx = Transaction('btc')
>>> tx.add_inputs_from_address(address='1HWpyFJ7N...', private_key='KxDwaDis...')
>>> tx.add_output('1Fs3...', 1.42, unit='btc')
>>> tx.fee(4000, unit='satoshi') #defaut is 10000
>>> tx.get_hex()
'00100137876876...
>>> tx.push()
```

The private key argument should be a string in WIF format.
You can also specify the `amount` argument to `add_output` with a unit argument:

```python
>>> tx.add_output(address, amount=1423, unit='bits')
>>> tx.add_output(address2, amount=1.3, units="usd")
```

All exchange rates are taken from the `get_current_price` function defined above.


## Push Transaction


If you have a raw transaction that you would like to push to the bitcoin network,
you can use moneywagon to do that:

```python
>>> from moneywagon import PushTx
>>> PushTx().push('btc', '0100000001d992c7a88...')
```

If the transaction went through successfully, the `push` method will return nothing.
This functionality works much like the others. If one service is down, it fallsback to another service.


## Fee Estimation


Moneywagon can be used to get the optimal fee to use for a transaction based on
the current state of the network.

```python
>>> from moneywagon import get_optimal_fee
>>> get_optimal_fee('btc', tx_bytes=213, acceptable_block_delay=0)
10650
```

In the above example, a transaction that is 213 bytes that is to be confirmed in
the next block, will need a fee of 10650 satoshis. If you are willing to wait
more blocks, call the function with `acceptable_block_delay` argument with the
number of blocks you're willing to wait until confirmation.

Currently, btc is the only currency supported for fee estimation.


# Advanced

## Controlling Service Redundancy via `service_mode`

Since all cryptocurrencies are open source, many of them have multiple instances
of block explorers running for public consumtion. These multiple services can
be utilized in various ways to gain various advantages.

Each blockchain function's high level API function call contains an optional keyword argument `service_mode`.
The mods are as follows:

* **default** - This method tris each service in order until it gets a valid response,
and then returns that response.

* **random** - This method is the same as the first, except the sources are randomized.

* **paranoid-2** - This method will call the first service, then the second service,
and then returns a response if the two responses are the same. If one API returns
a different value than another sevice, a `ServiceDisagreement` exception is raised.

* **paranoid-3...n** - Same as paranoid-2, except it calls three services and returns the value
if all three services agree. The number '3' an be replaced with any integer. You pass
in a number larger than the number of services programmed for that currency, then all
effectively all services are required to agree in order for a result to be returned.

```python
>>> from moneywagon import get_address_balance
>>> get_address_balance('btc', '1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X', service_mode='paranoid-2')
0.0002
```

In the above example, two calls will be made to two different services. One goes to the
first address balance service defined for BTC, and then another call will be made to the
second defined address balance service. In the case of the BTC currency, the first and second
services are BlockCypher and Blockr. To see which services are programmed to which
currencies, refer to the `crypto_data` module.

You can also pass in an explicit set of services:

```python
>>> from moneywagon import get_address_balance
>>> from moneywagon.services import Toshi, BlockchainInfo
>>> s = [Toshi, BlockchainInfo]
>>> get_address_balance('btc', '1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X', services=s, service_mode='random')
0.0002
```

In this example, one single call will be made to either Blockchain.info or Toshi (chosen at random).
If one of those services happens to be down at the monment, then the other one will be called and its
value returned.


## Low level API

The `get_current_price` function tries multiple services until it find one that returns a result.
If you would rather just use one service with no automatic retrying, use the low level 'service' API:

```python
>>> from moneywagon.services import BTER
>>> service = BTER()
>>> service.get_current_price('btc', 'usd')
(391.324, 'BTER')
```

Not all services will have every single possible function defined:

```
>>> service.get_historical_transactions('btc', 'blah')
** NotImplementedError: This service does not support getting historical_transactions.
Or rather it has no defined 'get_historical_transactions' method.
```

BTER is an exchange, not a block explorer, so it does not have a public API endpoint for getting
historical transactions. Most bock explorers don't have current price functionalities, etc.

If you use the `CurrentPrice` class, the `get` method will try all services
until a value is returned (same as the high level API). If you use a service class
that is limited to one API service, such as "BTER",
then only that service will be called.

You can also pass in a list of services classes to get more control of which
services will be used:

```python
>>> from moneywagon.services import BTCE, Bitstamp
>>> from moneywagon import CurrentPrice
>>> service = CurrentPrice(services=[BTCE, Bitstamp])
>>> service.get('btc', 'usd')
(377.2, 'btce')
```

## Caching considerations

The high level API does not do any caching of any sort. Each call to `get_current_price` will result in a
request with fresh results. On the other hand, the low level API will never make the request twice.

For instance, consider the following example:

```python
>>> from moneywagon.services import BTER
>>> service = BTER()
>>> service.get('ltc', 'rur') # makes two external calls, one for ltc->btc, one for btc->rur
(1.33535, 'bter')
>>> service.get('btc', 'rur') # makes zero external calls (uses btc-> rur result from last call)
(1.33535, 'bter')
```

Note that the BTER exchange does not have a direct orderbook between litecoin and Russian ruble.
As a result, pycryptoprices needs to make two separate API calls to get the correct exchange rate.
The first one to get the LTC->BTC exchange rate, and the second one to get the BTC->RUR exchange rate.
Then the two results are multiplied together to get the LTC -> RUR exchange rate.
If your application does a lot of converting at a time, it will be better for performance to use
the low level API.

If you keep the original service instance around and make more calls to get_price,
it will use the result of previous calls:

```python
>>> service.get('btc', 'rur') # will make no external calls
(17865.4210346, 'cryptonator')
```

In other words, if you are using the low level API and you want fresh values, you must make a new instance of the service class.


# Contributing


If you would like to add a new service, feel free to make a pull request.
If you discover a service is no longer working feel free to create a github issue and some will fix it shortly.


# Donations


If you would like to send a donation to support development, please send BTC here: 1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
