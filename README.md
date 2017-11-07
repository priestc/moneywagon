![Imgur](http://i.imgur.com/kLJqwqs.png)

# moneywagon


Moneywagon is a an implementation of a Blockchain Kernel. It is a tool that can be used
to built lightweight cryptocurrency wallets. Blockchain Kernels provide an
alternative to the outdated "SPV" method of building lightweight cryptocurrency
services.


## Features
* Lightweight wallet functionality - Use Moneywagon to build a bitcoin enabled device
Works on all cryptocurrencies, including BTC, LTC, PPC, DOGE, VTC, MYR.
    1. Get current crypto/fiat exchange rate
    2. Get crypto balance for address
    3. Get historical transactions for crypto address
    4. Get unspent outputs
    5. Get historical crypto/fiat price.
    6. Get optimal transaction fee (BTC only)
    7. Generate new crypto private/pubic keys supporting both 'WIF' and 'compressed' encodings.

General Cryptocurrency Features:
* Bip38 support
* Multi-sig support - coming soon
* HD-wallet support - coming soon

##  Prerequisites modules (for BIP38 & installation of module via pip)

```
$ pip install scrypt
$ pip install pycrypto
```

# Installation

```
$ pip install moneywagon
```

# Documentation

* [Supported Services](https://github.com/priestc/moneywagon/wiki/Supported-Services)
* [Exchange Operations](https://github.com/priestc/moneywagon/wiki/Exchange-Operations)
* [Blockchain Operations](https://github.com/priestc/moneywagon/wiki/Blockchain-Operations)
* [Command Line Interface](https://github.com/priestc/moneywagon/wiki/Command-Line-Interface)
* [Python Interface](https://github.com/priestc/moneywagon/wiki/Python-Interface)

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
This functionality works much like the others. If one service is down, it falls back to another service.


## Fee Estimation


Moneywagon can be used to get the optimal fee to use for a transaction based on
the current state of the network.

```python
>>> from moneywagon import get_optimal_fee
>>> get_optimal_fee('btc', tx_bytes=213)
10650
```

In the above example, a transaction that is 213 bytes that is to be confirmed in
the next block, will need a fee of 10650 satoshis.

Currently, btc is the only currency supported for fee estimation.

## Estimate coin supply

```python
>>> import datetime
>>> from moneywagon.supply_estimator import SupplyEstimator
>>> btc = SupplyEstimator('btc')
>>> btc.estimate_height_from_date(datetime.datetime(2014, 3, 12))
272736
>>> btc.calculate_supply(block_height=3244)
162200.0
>>> btc.calculate_supply(at_time=datetime.datetime(2017, 3, 12))
15882000.0
>>> ltc = SupplyEstimator('ltc')
>>> ltc.calculate_supply(block_height=320224)
16011200.0
```

Note that the `calculate_supply` function returns perfect results when estimating
from a block height. If estimating from `at_time`, then the results will be approximate.
The function `estimate_height_from_date` works by dividing the amount of time between
the passed in date and the genesis date of the currency, then dividing that amount of time
by the block interval. Because block are never found exactly every block interval,
the result of this calculation will be approximate.

# Advanced

## Finer control via "service modes"

Since all cryptocurrencies are open source, many of them have multiple instances
of block explorers running for public consumption. These multiple services can
be utilized in various ways to gain various advantages.

Each blockchain function's high level API function call accepts additional mode arguments.

* **random** - This method will randomize all sources so it doesn't always call the best service.

* **paranoid** - Integer 2 or greater - Paranoid mode means multiple services will be checked
and a result will only be returned if all services agree. The number passed in
is the number of services contacted. Default is 1.

* **average** - Integer 2 or greater. This mode will call the external service multiple
times and then return the average of returned results. Only applicable for functions that
return a single numerical value, such as `current_price`, and `get_optimal_fee`. For instance,
if you all `get_current_price` with `average=4`, 4 different services will be called to get current price,
the results will be averaged, and returned.

* **verbose** - True or False - If set to true, there will be extra debugging output

* **private** - Integer greater than 0. This mode is only applicable to endpoints that take multiple
addresses, (or a single extended public key). This will use a single service for each address. The
number passed in corresponds to the amount of seconds each of the external calls will be spread
out over. For instance, if you have 10 addresses you want the balance for, you use mode `private=4`
it will make those 10 different calls to 10 different services (chosen at random), and will spread them out
over a 4 second period. Currently this mode can not be used in tandem with `average` an `paranoid`
modes.

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
If one of those services happens to be down at the moment, then the other one will be called and its
value returned.

## Network Replay

This utility is used to mirror transactions from one network to another. Usage:

```
$ moneywagon network-replay btc bch latest --verbose`
```

This command will fetch the latest block from th BTC network, and then replay each
transaction to the BCH network. The word "latest" can be replaced with a block number
also. By default the first 5 transactions are attempted. To perform a full block replay,
append the `--limit=0` flag.

Currently only BCH and BTC are supported. Support for other forks will be added
eventually.

# Contributing


If you would like to add a new service, feel free to make a pull request.
If you discover a service is no longer working feel free to create a github issue and some will fix it shortly.


# Donations


If you would like to send a donation to support development, please send BTC here: 1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
