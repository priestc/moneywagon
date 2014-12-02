from __future__ import print_function

from .current_price import (
    CryptonatorCurrentPrice, BTERCurrentPrice, CoinSwapCurrentPrice,
    BitstampCurrentPrice, BTCECurrentPrice, CurrentPrice
)
from .address_balance import (
    BlockChainInfoAddressBalance, DogeChainInfoAddressBalance, BlockCypherAddressBalance,
    FeathercoinComAddressBalance, BlockrAddressBalance, AddressBalance
)
from .historical_price import (
    QuandlHistoricalPrice, HistoricalPrice
)
from .historical_transactions import (
    BlockrHistoricalTransactions, ChainSoHistoricalTransactions, HistoricalTransactions
)

def get_current_price(crypto, fiat):
    """
    High level function for getting the current price. This function will try multiple
    services until either a price is found, or if no price can be found, an exception is raised.
    """
    return CurrentPrice().get_price(crypto, fiat)
