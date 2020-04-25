'''
作者：纽润量化团队
问题分析：
    0. k线的构成要素： OHLC+Volume+顶部成交量+底部成交量+可触及的高点、低点
    1. 按照什么生成k线序列？
        1.1 按照等时间间隔，例如1分钟生成一根k线
        1.2 按照成交量，例如每100btc成交量生成一根k线，或者每100000美元生成一根k线
        1.3 按照笔数（存疑），例如每1000笔交易生成一根k线
        1.4 按照波动区间生成k线
    2.
'''

from packages import universal as UNIVERSAL
from packages import currency_pair as CP
from packages import data as DATA
from packages import plot as PLOT

currency_pair = CP.CurrencyPair()
trades = DATA.Data.from_db(
    'select * from trades_for_kraken order by timestamp')

# 测试根据成交量生成k线
# klines=UNIVERSAL.Klines.from_trades(currency_pair,trades,aggregated_by='volume',distance=100)

# 测试根据等价格间隔生成k线
# counter=0
# map={}
# for i in range(0,1):
#     distance=80+i*10
#     klines=UNIVERSAL.Klines.from_trades(currency_pair,trades,aggregated_by='equal_price',distance=distance)
#     counter=len(klines.klines)
#     map[str(distance)]=counter

# 测试根据等时间间隔生成k线
# klines=UNIVERSAL.Klines.from_trades(currency_pair,trades,aggregated_by='time',distance=60)

# 测试根据能预知未来的zigzag生成k线
# 仿真证明：30、40、50、60元区间段的获利最大
map={}
for distance in [86400]:
    # klines = UNIVERSAL.Klines.from_trades(currency_pair, trades, aggregated_by='zigzag', distance=distance)
    method='time'
    # klines = UNIVERSAL.Klines.from_trades(currency_pair, trades, aggregated_by='volume', distance=distance)
    klines = UNIVERSAL.Klines.from_trades(currency_pair, trades, aggregated_by=method, distance=distance)
    # map[str(distance)]=(len(klines.klines)*(distance-24),len(klines.klines)*(distance-11.2))
    # 测试数据写入数据库！！！！！请勿打开！！！！！！！！
    DATA.Data.to_db(klines,'klines_full_' + method + '_'+str(distance))

print(map)
# PLOT.plot_Klines(klines, auto_xaxis=True)
a = 1
