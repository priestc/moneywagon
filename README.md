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
  * [Service Support List](https://github.com/priestc/moneywagon/wiki/Exchange-Service-Support-Table)
* [Blockchain Operations](https://github.com/priestc/moneywagon/wiki/Blockchain-Operations)
* [Command Line Interface](https://github.com/priestc/moneywagon/wiki/Command-Line-Interface)
* [Python Interface](https://github.com/priestc/moneywagon/wiki/Python-Interface)
* [Creating Transactions](https://github.com/priestc/moneywagon/wiki/Creating-Transactions)
* [Service Modes](https://github.com/priestc/moneywagon/wiki/Service-Modes)
* [Tools](https://github.com/priestc/moneywagon/wiki/Tools)


# Contributing


If you would like to add a new service, feel free to make a pull request.
If you discover a service is no longer working feel free to create a github issue and some will fix it shortly.


# Donations


If you would like to send a donation to support development, please send BTC here: 1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
