![Imgur](http://i.imgur.com/kLJqwqs.png)

# moneywagon


Moneywagon is a partial implementation of the bitcoin protocol for both Python 2 and 3.
At it's current state, it is mostly a tool for building lightweight wallets,
but in the future there is plans for it to include all bitcoin operations such
as mining new blocks and relaying transaction as a full node.

In it's present form, think of moneywagon as a set of wrapper classes on top of
pybitcointools.

## Features
* Lightweight wallet functionality - Use monewagon to build a bitcoin enabled device
Works on all crytocurrencies, including BTC, LTC, PPC, DOGE, VTC, MYR.
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

# Installation

```
$ pip install moneywagon
```

# Supported APIs

To generate this list, with the most up-to-date service list, run the following command:

```
$ moneywagon service-table
```

<table>
<tr><th style="text-align: right;">  ID</th><th>Name             </th><th>URL                                                                                                                                  </th><th>Supported Currencies                                                                                                                                                                                                                                                                                                                  </th></tr>
<tr><td style="text-align: right;">   1</td><td>Bitstamp         </td><td><a href='https://www.bitstamp.net/api/' target='_blank'>https://www.bitstamp.net/api/</a>                                            </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">   2</td><td>BlockCypher      </td><td><a href='http://dev.blockcypher.com/' target='_blank'>http://dev.blockcypher.com/</a>                                                </td><td>btc, ltc, uro                                                                                                                                                                                                                                                                                                                         </td></tr>
<tr><td style="text-align: right;">   3</td><td>BlockSeer        </td><td><a href='https://www.blockseer.com/about' target='_blank'>https://www.blockseer.com/about</a>                                        </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">   4</td><td>SmartBitAU       </td><td><a href='https://www.smartbit.com.au/api' target='_blank'>https://www.smartbit.com.au/api</a>                                        </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">   5</td><td>Blockr           </td><td><a href='http://blockr.io/documentation/api' target='_blank'>http://blockr.io/documentation/api</a>                                  </td><td>btc, ltc, ppc, mec, qrk, dgc, tbtc                                                                                                                                                                                                                                                                                                    </td></tr>
<tr><td style="text-align: right;">   6</td><td>Toshi            </td><td><a href='https://toshi.io/docs/' target='_blank'>https://toshi.io/docs/</a>                                                          </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">   7</td><td>BTCE             </td><td><a href='https://btc-e.com/api/documentation' target='_blank'>https://btc-e.com/api/documentation</a>                                </td><td>                                                                                                                                                                                                                                                                                                                                      </td></tr>
<tr><td style="text-align: right;">   8</td><td>Cryptonator      </td><td><a href='https://www.cryptonator.com/api' target='_blank'>https://www.cryptonator.com/api</a>                                        </td><td>                                                                                                                                                                                                                                                                                                                                      </td></tr>
<tr><td style="text-align: right;">   9</td><td>Winkdex          </td><td><a href='http://docs.winkdex.com/' target='_blank'>http://docs.winkdex.com/</a>                                                      </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  11</td><td>ChainSo          </td><td><a href='https://chain.so/api' target='_blank'>https://chain.so/api</a>                                                              </td><td>doge, btc, ltc                                                                                                                                                                                                                                                                                                                        </td></tr>
<tr><td style="text-align: right;">  12</td><td>CoinPrism        </td><td><a href='http://docs.coinprism.apiary.io/' target='_blank'>http://docs.coinprism.apiary.io/</a>                                      </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  13</td><td>BitEasy          </td><td><a href='https://support.biteasy.com/kb' target='_blank'>https://support.biteasy.com/kb</a>                                          </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  14</td><td>BlockChainInfo   </td><td><a href='https://{domain}/api' target='_blank'>https://{domain}/api</a>                                                              </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  18</td><td>DogeChainInfo    </td><td><a href='https://dogechain.info/api' target='_blank'>https://dogechain.info/api</a>                                                  </td><td>doge                                                                                                                                                                                                                                                                                                                                  </td></tr>
<tr><td style="text-align: right;">  22</td><td>NXTPortal        </td><td><a href='https://nxtportal.org/' target='_blank'>https://nxtportal.org/</a>                                                          </td><td>nxt                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  23</td><td>CryptoID         </td><td><a href='https://chainz.cryptoid.info/api.dws' target='_blank'>https://chainz.cryptoid.info/api.dws</a>                              </td><td>dash, bc, bay, block, cann, uno, vrc, xc, uro, aur, pot, cure, arch, swift, karm, dgc, lxc, sync, byc, pc, fibre, i0c, nobl, gsx, flt, ccn, rlc, rby, apex, vior, ltcd, zeit, carbon, super, dis, ac, vdo, ioc, xmg, cinni, crypt, excl, mne, seed, qslv, maryj, key, oc, ktk, voot, glc, drkc, mue, gb, piggy, jbs, grs, icg, rpc, tx</td></tr>
<tr><td style="text-align: right;">  24</td><td>CryptapUS        </td><td><a href='https://cryptap.us/' target='_blank'>https://cryptap.us/</a>                                                                </td><td>nmc, wds, ber, scn, sc0, wdc, nvc, cas, myr                                                                                                                                                                                                                                                                                           </td></tr>
<tr><td style="text-align: right;">  25</td><td>BTER             </td><td><a href='https://bter.com/api' target='_blank'>https://bter.com/api</a>                                                              </td><td>                                                                                                                                                                                                                                                                                                                                      </td></tr>
<tr><td style="text-align: right;">  28</td><td>BitpayInsight    </td><td><a href='http://insight.bitpay.com/api' target='_blank'>http://insight.bitpay.com/api</a>                                            </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  30</td><td>MYRCryptap       </td><td><a href='http://insight-myr.cryptap.us/api' target='_blank'>http://insight-myr.cryptap.us/api</a>                                    </td><td>myr                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  31</td><td>BirdOnWheels     </td><td><a href='http://birdonwheels5.no-ip.org:3000/api' target='_blank'>http://birdonwheels5.no-ip.org:3000/api</a>                        </td><td>myr                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  32</td><td>ThisIsVTC        </td><td><a href='http://explorer.thisisvtc.com/api' target='_blank'>http://explorer.thisisvtc.com/api</a>                                    </td><td>vtc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  33</td><td>ReddcoinCom      </td><td><a href='http://live.reddcoin.com/api' target='_blank'>http://live.reddcoin.com/api</a>                                              </td><td>rdd                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  34</td><td>FTCe             </td><td><a href='http://block.ftc-c.com/api' target='_blank'>http://block.ftc-c.com/api</a>                                                  </td><td>ftc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  35</td><td>CoinTape         </td><td><a href='http://api.cointape.com/api' target='_blank'>http://api.cointape.com/api</a>                                                </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  36</td><td>BitGo            </td><td><a href='https://www.bitgo.com/api/' target='_blank'>https://www.bitgo.com/api/</a>                                                  </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  37</td><td>Blockonomics     </td><td><a href='https://www.blockonomics.co/views/api.html' target='_blank'>https://www.blockonomics.co/views/api.html</a>                  </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  38</td><td>BlockExplorerCom </td><td><a href='https://blockexplorer.com/api' target='_blank'>https://blockexplorer.com/api</a>                                            </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  40</td><td>BitcoinFees21    </td><td><a href='https://bitcoinfees.21.co/api' target='_blank'>https://bitcoinfees.21.co/api</a>                                            </td><td>btc                                                                                                                                                                                                                                                                                                                                   </td></tr>
<tr><td style="text-align: right;">  41</td><td>ChainRadar       </td><td><a href='http://chainradar.com/api' target='_blank'>http://chainradar.com/api</a>                                                    </td><td>aeon, bbr, bcn, btc, dsh, fcn, mcn, qcn, duck, mro, rd                                                                                                                                                                                                                                                                                </td></tr>
<tr><td style="text-align: right;">  42</td><td>Mintr            </td><td><a href='https://www.peercointalk.org/index.php?topic=3998.0' target='_blank'>https://www.peercointalk.org/index.php?topic=3998.0</a></td><td>ppc, emc                                                                                                                                                                                                                                                                                                                              </td></tr>
<tr><td style="text-align: right;">  43</td><td>BlockExplorersNet</td><td><a href='' target='_blank'></a>                                                                                                      </td><td>gsm, erc, tx                                                                                                                                                                                                                                                                                                                          </td></tr>
</table>




# Command Line Interface

## generate-keypair [crypto] [seed] [--password]

Generates a new private amd public keys, including hex and WIF encodings.
Optionally pass in a password that will be used to BIP38 encode the private key.

```
$ moneywagon generate-keypair btc SomERanDoMTexT --password=123 | python -mjson.tool
{
    "private": {
        "wif": "6PYVdYvBaMXD7bFNJwMh8DCTxcBQjzyPmqWDQDp2PBKYyFUACph7vzjeaN"
    },
    "public": {
        "address": "1BrUfC75qyLQxxp7qcisfaMmwRMECo4ETC",
        "hex": "037a7e546b2d9ecd9aa99d63c5d6eb4b4cc6880a6a7df8a02a2d83bc4e6b1022ab",
        "hex_uncompressed": "047a7e546b2d9ecd9aa99d63c5d6eb4b4cc6880a6a7df8a02a2d83bc4e6b1022abcd2a6af5c8e36d74779e23d6be11fc0aaf923b7269d2d43b39dc970df8e98449"
    }
}
$ moneywagon generate-keypair btc SomERanDoMTexT | python -mjson.tool
{
    "private": {
        "hex": "c1fb6c4ccd6e6646e2ffea8608f67450ac98e64b26b748ad963ae22fc13367ed01",
        "hex_uncompressed": "c1fb6c4ccd6e6646e2ffea8608f67450ac98e64b26b748ad963ae22fc13367ed",
        "wif": "L3inayCqKqXUbu3yUHxjqWSurW5pc7bXEbwJCqUhEPfUqkTzhsgz",
        "wif_uncompressed": "5KHibRy9gcTqr9Ajhd1r8NAx2FHxC8PKdcZEsG4ZE19iepmCS8x"
    },
    "public": {
        "address": "1BrUfC75qyLQxxp7qcisfaMmwRMECo4ETC",
        "hex": "037a7e546b2d9ecd9aa99d63c5d6eb4b4cc6880a6a7df8a02a2d83bc4e6b1022ab",
        "hex_uncompressed": "047a7e546b2d9ecd9aa99d63c5d6eb4b4cc6880a6a7df8a02a2d83bc4e6b1022abcd2a6af5c8e36d74779e23d6be11fc0aaf923b7269d2d43b39dc970df8e98449"
    }
}
```

The seed can be any string, preferably with a lot of entropy.
You can also pipe in entropy via standard input by specifying a dash for the seed:

```
$  openssl rand 10000 | moneywagon generate-keypair ppc - | python -mjson.tool
{
    "private": {
        "hex": "a937be15ff2e7b9313c38714d608180d2ae9a8732e91adead3f666da51bee03301",
        "hex_uncompressed": "a937be15ff2e7b9313c38714d608180d2ae9a8732e91adead3f666da51bee033",
        "wif": "UAnKzDUDpKorVCCLcL4yjPvVM3RstB8NaqE5VSVvipg1DSyEB7WU",
        "wif_uncompressed": "7A1kixqm91BcgU1JaqGrZGAQBtJRDW2fsiHZHQuKWsDv4nGD5jq"
    },
    "public": {
        "address": "PWCL5zURy3aeGdpH4tu1NBVMkPyKMm3Hwk",
        "hex": "0392a2b02487ae4b0a0a23aaab27573d40643e9aa64fe2b8822b190c01b0b04311",
        "hex_uncompressed": "0492a2b02487ae4b0a0a23aaab27573d40643e9aa64fe2b8822b190c01b0b0431149b353eecdd3cac0de024835a22021b84a12ba820918786e67c185e13d8b4887"
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

Also you can include a `--verbose` flag to get more output:

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

## single-transaction [crypto] [txid]

```
$ moneywagon single-transaction ppc 6dddc4deb0806d987844b429e73b20ce5f0355407cce220130b5eac8fa13970e | python -mjson.tool
{
    "block_number": 117284,
    "confirmations": 115918,
    "fee": 0.02,
    "inputs": [
        {
            "address": "PJyL5yc5Zk2EDC2p4Tu5fAfU5NP59hDn88",
            "amount": 1.001288
        },
        {
            "address": "PJopCzzaHC1Kb1CV7iDLs1o4gXpssG1czj",
            "amount": 0.010604
        },
        {
            "address": "PGBnz34C79DahgY5pEN5zdSwkkeEZBH7n2",
            "amount": 0.010862
        },
        {
            "address": "PGXvsTrer2neCnhwCk9FwMJxHTcfznoYKk",
            "amount": 100.01
        },
        {
            "address": "PJyL5yc5Zk2EDC2p4Tu5fAfU5NP59hDn88",
            "amount": 1.137068
        },
        {
            "address": "PJyL5yc5Zk2EDC2p4Tu5fAfU5NP59hDn88",
            "amount": 1.056389
        },
        {
            "address": "PDsudZAz7F7XvB6x5h5oyoNT35uLRXuwrf",
            "amount": 0.78484
        }
    ],
    "outputs": [
        {
            "address": "PEWcuiycc1vaSqAVBC5bpGq2mMF7Gs4ixp",
            "amount": 0.011051
        },
        {
            "address": "PVoei4A3TozCSK8W9VvS55fABdTZ1BCwfj",
            "amount": 103.98
        }
    ],
    "time": "2014-06-16T00:07:10+00:00",
    "total_in": 104.01105100000001,
    "total_out": 103.991051,
    "txid": "6dddc4deb0806d987844b429e73b20ce5f0355407cce220130b5eac8fa13970e"
}
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

## sweep [crypto] [private_key] [to_address] [--fee=optimal|n] [--password]

Send all funds associated with `private_key` and send them to `to_address`.
Optionally specify what fee you would like to include. Can either be an integer
in satoshis, or the string 'optimal'. Returned is the txid of the broadcasted
transaction.

Use `--password` if your private key is encoded with a BIP38 password.

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

## wallet-balance [wallet path] [fiat] [--async] [--collapse]

Get the fiat total of a group of cryptocurrency addresses from a "csv wallet" file.

The `--async` option will do all the price and blockchain fetches asynchronusly
so the operation finishes much faster. The `--collapse` option will sum all balances
of the same currency to the same line on output.

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
391.324
>>> get_current_price('ltc', 'rur', report_services=True)
([<Service: BTCE (1 in cache)>], 226)
```

A float is always returned. Older versions of moneywagon returned a two item tuple.
Starting with moneywagon version 1.9.0, only a float is retuened. If your application needs
to know which service was used, set the `report_services` argument to `True`. (See example above).

If an external service is down, the net service in the chain is tried, until a result is found.

If the API has changed, or the currency pairs is not implemented, an exception will be raised:

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
>>> service.action('btc', 'usd', '2013-11-13')
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
>>> service.action('vtc', 'rur', '2014-11-13'))
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
>>> AddressBalance().action('ppc', 'PVoei4A3TozCSK8W9VvS55fABdTZ1BCwfj')
103.98
```

## Block Explorer URLs

Some services have a web interface for viewing blockchain data in a web browser.
To get a list of all block explorer urls, use the fllowing API:

```
$ moneywagon explorer-urls btc --address=1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
http://blockr.io/address/info/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X https://chain.so/address/btc/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X https://www.biteasy.com/blockchain/addresses/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X https://www.smartbit.com.au/address/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X https://blockchain.info/address/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X https://insight.bitpay.com/address/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
```

You can pipe these URLs directly into a browser:

```
$ moneywagon explorer-urls btc --address=1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X | xargs firefox -new-tab -url "$line"
```

Or through python:

```python
>>> from moneywagon import get_explorer_url
>>> get_explorer_url('btc', address='1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X')
[
 "http://blockr.io/address/info/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X",
 "https://chain.so/address/btc/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X",
 "https://www.biteasy.com/blockchain/addresses/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X",
 "https://www.smartbit.com.au/address/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X",
 "https://blockchain.info/address/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X",
 "https://insight.bitpay.com/address/1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X"
]

```

## Get Blocks

```python
>>> from moneywagon import get_block
>>> get_block('btc', latest=True)
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
>>> get_block('btc', block_number=242)
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
>>> get_block('doge', block_hash='a53d288822382a53250b930193562b7e61b218c8a9a449a9d003dafa2534a736')
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
>>> HistoricalTransactions().action('ltc', 'Lb78JDGxMcih1gs3AirMeRW6jaG5V9hwFZ')
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
>>> get_optimal_fee('btc', tx_bytes=213)
10650
```

In the above example, a transaction that is 213 bytes that is to be confirmed in
the next block, will need a fee of 10650 satoshis.

Currently, btc is the only currency supported for fee estimation.


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
If one of those services happens to be down at the monment, then the other one will be called and its
value returned.

## Utilities

```python
>>> from moneywagon import guess_currency_from_address
>>> guess_currency_from_address("NJwRrtKcv3ggkwh3j3yka69rH3x5d5gu5m")
[['nmc', 'Namecoin']]
>>> guess_currency_from_address("1Ng3mALXCEphwLqTZ4x5DutMcRTxpTF299")
[['btc', 'Bitcoin']]
>>> guess_currency_from_address("EMZSp8Q3MGHZmjhSBvh52r6igstTDo4Jzx")
[['emc', 'Emercoin'], ['erc', 'Europecoin']]

```

This can be used as an address verifier, as an exception gets raised when an invalid
address is passed in.

## Low level API

The `get_current_price` function tries multiple services until it find one that returns a result.
If you would rather just use one service with no automatic retrying, use the low level 'service' API:

```python
>>> from moneywagon.services import BTER
>>> service = BTER()
>>> service.get_current_price('btc', 'usd')
391.324
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
1.33535
>>> service.get_current_price('btc', 'rur') # makes zero external calls (uses btc-> rur result from last call)
1.33535
```

Note that the BTER exchange does not have a direct orderbook between Litecoin and Russian Ruble.
As a result, moneywagon needs to make two separate API calls to get the correct exchange rate.
The first one to get the LTC->BTC exchange rate, and the second one to get the BTC->RUR exchange rate.
Then the two results are multiplied together to get the LTC -> RUR exchange rate.
If your application does a lot of converting at a time, it will be better for performance to use
the low level API.

If you keep the original service instance around and make more calls to get_price,
it will use the result of previous calls:

```python
>>> service.get_current_price('btc', 'rur') # will make no external calls
17865.4210346
```

In other words, if you are using the low level API and you want fresh values, you must make a new instance of the service class.


# Contributing


If you would like to add a new service, feel free to make a pull request.
If you discover a service is no longer working feel free to create a github issue and some will fix it shortly.


# Donations


If you would like to send a donation to support development, please send BTC here: 1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
