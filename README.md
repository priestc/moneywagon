![Imgur](http://i.imgur.com/kLJqwqs.png)

# moneywagon


Moneywagon is a partial implementation of the bitcoin protocol written in Python.
At it's current state, it is mostly a tool for building lightweight wallets,
but in the future there is plans for it to include all bitcoin operations such
as mining new blocks and relaying transaction as a full node.

In it's present form, think of moneywagon as a set of wrapper classes on top of
pybitcointools.

## Features
A. Lightweight wallet functionality - Use monewagon to build a bitcoin enabled device
Works on all crytocurrencies, including BTC, LTC, PPC, DOGE, VTC, MYR.
    1. Get current crypto/fiat exchange rate
    2. Get crypto balance for address
    3. Get historical transactions for crypto address
    4. Get unspent outputs
    5. Get historical crypto/fiat price.

B. Bip38 support - coming soon
C. Multi-sig support - coming soon
D. DHwallet support - coming soon

# Installation

```
$ pip install moneywagon
```

# Command Line Interface

There are currently 6 functions available through the command line interface:

## generate-keypair [crypto] [seed]

Generates a new private amd public keys, including hex and WIF encodings.

```
$ moneywagon generate-keypair btc SomERanDoMTexT | python -mjson.tool
{
    "private": {
        "hex": "c1fb6c4ccd6e6646e2ffea8608f67450ac98e64b26b748ad963ae22fc13367ed",
        "wif": "5KHibRy9gcTqr9Ajhd1r8NAx2FHxC8PKdcZEsG4ZE19iepmCS8x"
    },
    "public": {
        "address": "1ACQLPrD3674whw5AP37T5NjbYdQ3XSuEF",
        "hex": "047a7e546b2d9ecd9aa99d63c5d6eb4b4cc6880a6a7df8a02a2d83bc4e6b1022abcd2a6af5c8e36d74779e23d6be11fc0aaf923b7269d2d43b39dc970df8e98449"
    }
}
```

The seed can be any string, preferably with a lot of entropy.
You can also pipe in entropy via standard input by specifying a dash for the seed:

```
$ date | md5sum | moneywagon generate-keypair ppc - | python -mjson.tool
{
    "private": {
        "hex": "feb07aad450159cd9ead9bb702a6151fae93a02f88d19001ebc425ec350c04de",
        "wif": "7AfPyvoLenqb1KAD78JdGvfJecm3ZkEoks9mjj1wqdkDKsC4BUS"
    },
    "public": {
        "address": "PWmtVPtoXmYDEixmCTFvwd4eNRCYEZaGgQ",
        "hex": "044cfaadd71d8c90fc0f5ef73eb47dd2c0fa74d6259476e0aa23e0c4fe10418cc6a68694665cd56f3222118249e40fafffa55239390d65f168bdfb837726f97e09"
    }
}
```

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
$ moneywagon address-balance doge D8ZXs3JDdLuyRjG3wDtRQE2PMT4YQWELfZ
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

## get-block [crypto] [--block_number=n|--block_hash=hash|--latest]

Gets the block, according to either block number, block hash or get by latest.

example:

```
$ moneywagon get-block btc --latest --paranoid=2 | python -m json.tool
{
    "block_number": 368900,
    "confirmations": 1,
    "hash": "0000000000000000043ab9d01e2e88ff460b6205b43cf3508ddeb8461bddc2fd",
    "merkle_root": "7205cd649ffe5645e1841ef2ba19d7c48166dc9a6f15584aa24d4af61236d96e",
    "mining_difficulty": 52278304845.59181,
    "next_hash": null,
    "previous_hash": "00000000000000000f3a1d9508d69a1310a1ed41e18025f143f28c8ea5f5575e",
    "sent_value": 8762.56646775,
    "size": 219868,
    "time": "2015-08-08T05:55:01+00:00",
    "total_fees": 0.07663532,
    "txids": [
      "da8812c9c7e02d4c159bc2c9978aa50dd295d88fe14f10e07101c729e771510e",
      "ce6c456ecf46be306eb65eb9ac8210466d6aacd0e44b8dfdeaf100d9aaadca47",
      ...
    ]
}
$ moneywagon get-block ltc --block_number=242 | python -m json.tool
{
    "block_number": 242,
    "confirmations": 829724,
    "hash": "3849a1aabc09d147d815652cadee10b55f8eddf63efe4174479dba7e74d76cf1",
    "merkle_root": "30a914ec415904b0dac0cf9bf5eed275b721cbb87a757878bc6d425817c52027",
    "mining_difficulty": 0.00024414,
    "next_hash": "1f427c34e3d98d7d0eb205be0881ea15d49c5e41f3d783e345f30747d2baad3b",
    "previous_hash": "a6af6882076ece122753d12c134815f33b2b3f3d9e8feeeb5529f6ec5ef3b31c",
    "sent_value": 50.0,
    "size": 215,
    "time": "2011-10-13T03:13:40+00:00",
    "total_fees": 0.0,
    "txids": [
      "da8812c9c7e02d4c159bc2c9978aa50dd295d88fe14f10e07101c729e771510e",
      "ce6c456ecf46be306eb65eb9ac8210466d6aacd0e44b8dfdeaf100d9aaadca47",
      ...
    ]
}

```

## sweep [crypto] [private_key] [to_address] [--fee=optimal|n]

Send all funds associated with `private_key` and send them to `to_address`.
Optionally specify what fee you would like to include. Can either be an integer
in satoshis, or the string 'optimal'. Returned is the txid of the broadcasted
transaction.

```
moneywagon moneywagon sweep btc 812b... 1Coq3qrShpWQNZ7yGCREo6EqUCdem4EdtJ --fee=optimal --verbose
['02491bdced5e48734de7c922547f1e73b4706d3747143ed01934d75313161c42']
```

## historical-transactions [crypto] [address]

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

## wallet-balance [wallet path] [fiat]

Get the fiat total of a group of cryptocurrency addresses from a "csv wallet" file.

example:

```
$ cat ~/wallets.csv
doge,D8ZXs3JDdLuyRjG3wDtRQE2PMT4YQWELfZ
btc,1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
$ moneywagon wallet-balance ~/wallets.csv usd
doge (16.43 USD) == 99405.6048377 x 0.00016531 (cryptonator)
btc (1.06 USD) == 0.00379546 x 279.58 (bitstamp)
Total amount of all crypto: 17.49 USD
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
datetime object by ``arrow.get``

```python
>>> from moneywagon import HistoricalCryptoPrice
>>> service = HistoricalCryptoPrice()
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

## Get Blocks

```
>>> from moneywagon import get_blocks
>>> get_blocks('btc', latest=True)
{
    "block_number": 368900,
    "confirmations": 1,
    "hash": "0000000000000000043ab9d01e2e88ff460b6205b43cf3508ddeb8461bddc2fd",
    "merkle_root": "7205cd649ffe5645e1841ef2ba19d7c48166dc9a6f15584aa24d4af61236d96e",
    "mining_difficulty": 52278304845.59181,
    "next_hash": null,
    "previous_hash": "00000000000000000f3a1d9508d69a1310a1ed41e18025f143f28c8ea5f5575e",
    "sent_value": 8762.56646775,
    "size": 219868,
    "time": "2015-08-08T05:55:01+00:00",
    "total_fees": 0.07663532,
    "txids": [
      "da8812c9c7e02d4c159bc2c9978aa50dd295d88fe14f10e07101c729e771510e",
      "ce6c456ecf46be306eb65eb9ac8210466d6aacd0e44b8dfdeaf100d9aaadca47",
      ...
    ]
}
>>> get_blocks('btc', block_number=242)
{
    "block_number": 242,
    "confirmations": 829724,
    "hash": "3849a1aabc09d147d815652cadee10b55f8eddf63efe4174479dba7e74d76cf1",
    "merkle_root": "30a914ec415904b0dac0cf9bf5eed275b721cbb87a757878bc6d425817c52027",
    "mining_difficulty": 0.00024414,
    "next_hash": "1f427c34e3d98d7d0eb205be0881ea15d49c5e41f3d783e345f30747d2baad3b",
    "previous_hash": "a6af6882076ece122753d12c134815f33b2b3f3d9e8feeeb5529f6ec5ef3b31c",
    "sent_value": 50.0,
    "size": 215,
    "time": "2011-10-13T03:13:40+00:00",
    "total_fees": 0.0,
    "txids": [
      "da8812c9c7e02d4c159bc2c9978aa50dd295d88fe14f10e07101c729e771510e",
      "ce6c456ecf46be306eb65eb9ac8210466d6aacd0e44b8dfdeaf100d9aaadca47",
      ...
    ]
}
>>> get_blocks('doge', block_hash='a53d288822382a53250b930193562b7e61b218c8a9a449a9d003dafa2534a736')
{
    "block_number": 242,
    "confirmations": 824212,
    "hash": "a53d288822382a53250b930193562b7e61b218c8a9a449a9d003dafa2534a736",
    "merkle_root": "83d53e8dbbfdcf9e24a1ece401801e73a430db9c80da2ca3f74dc3b73c18abbf",
    "mining_difficulty": 0.00024414,
    "next_hash": "1aca39498439acff59afbabb6992bf9fa178415674415283f8a127120211a3dd",
    "previous_hash": "bb623eabcde58af2b3a412eb9866f54f414d5eef1de5f54bd6e396834c8ccc75",
    "sent_value": 790312.0,
    "size": 190,
    "time": "2013-12-08T04:07:20+00:00",
    "total_fees": 0.0,
    "txids": [
      "da8812c9c7e02d4c159bc2c9978aa50dd295d88fe14f10e07101c729e771510e",
      "ce6c456ecf46be306eb65eb9ac8210466d6aacd0e44b8dfdeaf100d9aaadca47",
      ...
    ]
}

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
>>> tx.add_inputs(private_key='KxDwaDis...')
>>> tx.add_output('1Fs3...', 1.42, unit='btc')
>>> tx.fee(4000, unit='satoshi') #defaut is 10000
>>> tx.get_hex() # call this method to see the tx in hex format
'00100137876876...
>>> tx.push()
```

You can pass in a paranoid parameter to the Transaction constructor that will make
all external service calls cross checked. By default, all service calls are
only performed once. You can increase this value to get more assurance that your
blockchain source has not been compromised.

```python
>>> tx = Transaction('btc', paranoid=2)
```

Or if you want more fine control over which inputs go in:

```python
>>> my_inputs = get_unpent_outputs('1PZ3Ps9Rv...')[:2] # just the first two
>>> tx.add_raw_inputs(my_inputs, 'KdEr5D1a...')
>>> more_inputs = [x for x in get_unpent_outputs('1HWpyFJ7N...') if x['amount'] < 10000]]
>>> tx.add_raw_inputs(more_inputs, 'KxDwaDis...')
>>> tx.add_output('1Fd3...', 1.42, unit='btc')
>>> tx.push()
```

The last input that is added (either through `add_raw_inputs` or `add_inputs`)
will be used as the change address. You can manually specify a change address by modifying
the value of `tx.change_address` before calling `tx.push()`.


```python
>>> tx.add_inputs(address='1HWpyFJ7N...', private_key='KxDwaDis...')
>>> tx.add_output('1Fd3...', 1.42, unit='btc')
>>> tx.change_address = '1PZ3Ps9Rv...' # replace change address from 1HWpyFJ... -> 1PZ3Ps9Rv...
>>> tx.push()
```

The private key argument should be a string in hex format.
You can also specify the `amount` argument to `add_output` with a unit argument:

```python
>>> tx.add_output(address, amount=1423, unit='bits')
>>> tx.add_output(address2, amount=1.3, units="usd")
```

All exchange rates are taken from the `get_current_price` function defined above.

Currently there is no way to decode transactions using moneywagon.
One day this feature will get added.

You can also make unsigned transactions by passing in just the address to the
`add_inputs` function. You must also pass in `signed=False` to the `get_hex`
function. This hex can't be pushed to the network until it has been signed.

```python
>>> tx.add_inputs(address='1HWpyFJ7N...')
>>> tx.add_output('1Fd3...', 1.42, unit='btc')
>>> tx.get_hex(signed=False)
'00100137876876...
```

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

## Finer control via "service modes"

Since all cryptocurrencies are open source, many of them have multiple instances
of block explorers running for public consumption. These multiple services can
be utilized in various ways to gain various advantages.

Each blockchain function's high level API function call accepts additional mode arguments.

* **random** - This method will randomize all sources so it doesn't always call the best service.

* **paranoid** - Integer 1 or greater - Paranoid mode means multiple services will be checked
and a result will only be returned if all services agree. The number passed in
is the number of services contacted. Default is 1.

* **verbose** - True or False - If set to true, there will be extra debugging output

```python
>>> from moneywagon import get_address_balance
>>> get_address_balance('btc', '1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X', paranoid=2, random=True)
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
>>> get_address_balance('btc', '1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X', services=s, random=True)
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

If you use the `CurrentPrice` class, the `action` method will try all services
until a value is returned (same as the high level API). If you use a service class
that is limited to one API service, such as "BTER",
then only that service will be called.

You can also pass in a list of services classes to get more control of which
services will be used:

```python
>>> from moneywagon.services import BTCE, Bitstamp
>>> from moneywagon import CurrentPrice
>>> service = CurrentPrice(services=[BTCE, Bitstamp])
>>> service.action('btc', 'usd')
(377.2, 'btce')
```

## Caching considerations

The high level API does not do any caching of any sort. Each call to `get_current_price` will result in a
request with fresh results. On the other hand, the low level API will never make the request twice.

For instance, consider the following example:

```python
>>> from moneywagon.services import BTER
>>> service = BTER()
>>> service.get_current_price('ltc', 'rur') # makes two external calls, one for ltc->btc, one for btc->rur
(1.33535, 'bter')
>>> service.get_current_price('btc', 'rur') # makes zero external calls (uses btc-> rur result from last call)
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
>>> service.get_current_price('btc', 'rur') # will make no external calls
(17865.4210346, 'cryptonator')
```

In other words, if you are using the low level API and you want fresh values, you must make a new instance of the service class.


# Contributing


If you would like to add a new service, feel free to make a pull request.
If you discover a service is no longer working feel free to create a github issue and some will fix it shortly.


# Donations


If you would like to send a donation to support development, please send BTC here: 1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
