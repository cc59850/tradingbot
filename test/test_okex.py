from packages import okex as OKEX
from packages import currency_pair as CP

okex=OKEX.Okex(None)
cp=CP.CurrencyPair('btc','usdt')
trades=okex.trades(currency_pair=cp)
a=1
