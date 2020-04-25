from  packages import binance as B
from packages import currency_pair as CP
from packages import account as ACC
import time

account=ACC.Account('gBAyXDQx4SWJ1FKI5cG4xaYJVwTNnMWUVcrvHjNVAKjxmt0JrpLpowQ85Kg49Ak9','EZaHgc67HCNeniUGiLbTBHZJyYsq5MyVPuwOugXUSeTz1mKma1wWaPm3yTeAN7En')
binance=B.Binance(account)
trades=binance.trades(CP.CurrencyPair())
starting_timestamp=0
ending_timestamp=time.time()
while starting_timestamp<ending_timestamp:
    pass
a=1