'''
根据每笔成交订单统计订单价格的分布规律

'''

from packages import db as DB
import CONSTANTS
import matplotlib.pyplot as plt

pgmanager = DB.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)
rows = pgmanager.select('select * from trades_for_kraken')
max = pgmanager.select('select max(price) from trades_for_kraken')[0][0]
min = pgmanager.select('select min(price) from trades_for_kraken')[0][0]
max = int(max/10) + 1
min = int(min/10)
buys = {}
sells = {}
for cnt in range(min, max + 1):
    buys[cnt] = 0
    sells[cnt] = 0

for row in rows:
    price = int(row[5]/10)
    amount = row[6]
    trade_type = row[4]
    if trade_type == 1:
        buys[price] += amount
    else:
        sells[price] += amount

prices = sorted(buys.keys())
buys1, sells1 = [], []
for price in prices:
    buys1.append(buys[price])
    sells1.append(-sells[price])

a = 1

fig,ax1=plt.subplots(1, sharex=True, figsize=(32, 15))
plt.bar(prices,buys1 )
plt.bar(prices,sells1)
plt.show()
