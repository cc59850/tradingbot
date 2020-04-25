from packages import data as DATA
from packages import plot as PLOT
from packages import universal as UNIVERSAL
from packages import currency_pair as CP
import matplotlib.pyplot as plt
import mpl_finance as mpf
from packages import db as DB
import CONSTANTS
import datetime
from matplotlib.pylab import date2num
from matplotlib.widgets import Cursor

pgmanager=DB.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)
tablename='klines_full_vol_50'

rows=pgmanager.select('select * from '+tablename + ' where timestamp>1577808000+86400*5 order by timestamp limit 300')
a=1

alist = []
vols_bid = []
vols_ask = []
diff_bid_2_ask = []
diff_bid_2_ask_in_past_2_epochs = []
diff_bid_2_ask_in_past_3_epochs = []
diff_bid_2_ask_in_past_5_epochs = []
diff_bid_2_ask_in_past_10_epochs = []
diff_bid_2_ask_in_past_20_epochs = []
avg_buys=[]
avg_sells=[]
avg_buy_diff_sell=[]
avg_amounts=[]
dates = []
cnt = 0
date = date2num(datetime.datetime.fromtimestamp(rows[0][1]))

for cnt in range(20, len(rows)):
    row_previous2=rows[cnt-2]
    row_previous1 = rows[cnt - 1]
    row = rows[cnt]
    open=row[2]
    high=row[3]
    low=row[4]
    close=row[5]
    vol=row[6]
    vol_buy,vol_sell=row[7:9]
    avg_buy, avg_sell, avg_amount_per_trade=row[-3:]
    date = date + 1
    data = (date, open, high, low, close)
    alist.append(data)
    vols_bid.append(-vol_buy)
    vols_ask.append(vol_sell)
    diff_bid_2_ask.append(vol_buy-vol_sell)
    diff_bid_2_ask_in_past_2_epochs.append(
        vol_buy + row_previous1[7] - vol_sell-row_previous1[8])
    diff_bid_2_ask_in_past_3_epochs.append(
        vol_buy + row_previous1[7] +row_previous2[7] - vol_sell-row_previous1[8]-row_previous2[8])
    avg_buy_diff_sell.append(avg_buy-avg_sell)
    avg_amounts.append(avg_amount_per_trade*100)
    dates.append(date)

# fig, ax = plt.subplots(figsize=(32, 18))
# fig.subplots_adjust(bottom=0.5)
# mpf.candlestick_ohlc(ax, alist, width=0.5, colorup='g', colordown='r', alpha=1.0)
# plt.grid(True)
# # 设置日期刻度旋转的角度
# plt.xticks(rotation=30)
# plt.title('wanda yuanxian 17')
# plt.xlabel('Date')
# plt.ylabel('Price')
# # x轴的刻度为日期
# ax.xaxis_date()

fig, axes = plt.subplots(3, sharex=True, figsize=(64, 30))
mpf.candlestick_ohlc(axes[0], alist, width=0.5, colorup='g', colordown='r')

axes[0].set_title('BTC')
axes[0].set_ylabel('价格')
axes[0].grid(True)
axes[0].xaxis_date()

# axes[1].plot(dates, avg_buy_diff_sell,c='red',linewidth=0.5)
# axes[1].plot(dates, avg_amounts,c='green', linewidth=0.5)
# axes[1].grid(True)
axes[1].plot(dates, avg_buy_diff_sell, c='orange')
axes[1].plot(dates, avg_amounts, c='blue')
axes[1].set_ylabel('成交量')
axes[1].grid(True)

axes[2].plot(dates, diff_bid_2_ask, c='green')
axes[2].plot(dates, diff_bid_2_ask_in_past_2_epochs, c='orange')
axes[2].plot(dates, diff_bid_2_ask_in_past_3_epochs, c='blue')
axes[2].set_ylabel('成交量')
axes[2].grid(True)

axes[2].set_ylabel('买卖均价')
axes[2].grid(True)

plt.show()