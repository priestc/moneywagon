Moneywagon SPV Whitepaper
=========================

Abstract
--------

When Satoshi released his bitcoin witepaper in 2009, he included a section
called "Simple Payment Verfication". This scheme was a method for building
a bitcoin wallet application without needing to keep a local copy of the bitcoin
blockchain.

I believe Satoshi's scheme was sufficient for the ecosystem that existed at the time,
but in 2015 the bitcoin ecosystem has grown by orders of magnitude.

With this white paper, I propose another more modern method of architecting
lightweight wallets that leveraging the massive bitcoin ecosystem.


Drawbacks of traditional "Satoshi style" SPV
--------------------------------------------

Bitcoin in 2009 was very small. The code has to contend with the fact that
anyone could run their own custom "hacked" version of bitcoin to mess up the network.
For this reason, bitcoin has to go through great lengths to incentivising correct behavior.
Each node is anonymous. For this reason, no data from any node can be trusted unless you verify the math yourself.
In order to do this math, you need the entire blockchain stored on your computer.
This blockchain is currently 20GB and will grow to be orders of magnitude larger than it already is in the future.

Satoshi style SPV essentially works by having the wallet only download block headers, instead of the entire block.
The math can then be calculated off the block headers, using a method called "merkle roots".

There still exist one problem. You have to download these block headers from someone, and
with satoshi style SPV, you download them from anonymous bitcoin nodes. You essentially have to trust the
anonymous network to not send you fake data.

Moneywagon SPV solves this problem by not downloading anything from anonymous nodes.
All the data it gets comes from trusted nodes.

What is a trusted node?
-----------------------

A trusted node is a bitcoin full node that has a name and reputation behind it.
One such example is blockchain.info. Another example of Blockr.io.
These 'entities' have a name, a url, and a blockchain available through a public API
that anyone can use to make a wallet. There are currently dozens of such services.
As time goes on, and the bitcoin ecosystem grows, there are many more blockchain APIs
that are expected to appear.

Essentially each business doing business using the blockchain is incentivized to run their own node.


Choice == Freedom
-----------------

Since there are multiple trusted blockchain APIs available, users are free to switch between
different service API providers. For instance a user could have a wallet that runs on blockchain.info,
but for some reason maybe blockchain.info destroys user's trust, the user is free to switch to,
for instance chain.so. The likelyhood that every single blockchain API in existence is
compromised is very slim.


Altcoin support
---------------

Since the majority of full node software is easily extended to support bitcoin
forks, (or altcoins as they are known), it is very easy to build multi-currency wallets
using a moneywagon archetecture. For instance, if you wanted to add support for a
new currency to yout moneywagon wallet, you could theoretically add that currency to
the moneywagon codebase with less than 10 lines of code.


"Paranoid mode" - A new kind of consensus
-----------------------------------------

Moneywagon performs operations using a redundant fetching scheme called "Paranoid mode".
The purpose of this mode is to verify the there exist multiple trusted nodes that have agreeing data.
When you call any method, you can specify which level of "paranoia" you prefer.

If you want to use paranoid=4, data will only get returned if there are 4 additional
services that return the same data. If any one service returns anything different, the
call fails. The user is presented with an error message that the network is experiencing problems.

With sufficient paranoia, it can be assumed that your wallet will never produce fraudulent
transactions causing the wallet user to lose money.


Implementations
===============

Currently there is one implementation of a wallet using this method.
The library is called moneywagon and it is on github and pypi.
