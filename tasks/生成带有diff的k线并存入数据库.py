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
from packages import db as DB
import CONSTANTS

tablename='klines_full_time_86400'
mypgmanager=DB.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)
rows=mypgmanager.select('select * from '+tablename+' order by timestamp')
len_rows=len(rows)

sqls=[]
for cnt1 in range(50,len_rows):
    if cnt1%10000==0:
        print("已完成",cnt1/len_rows*100,"%")
    row=rows[cnt1]
    timestamp=row[1]
    open=row[2]
    high=row[3]
    low=row[4]
    close=row[5]
    vol=row[6]
    vol_buy=row[7]
    vol_sell=row[8]
    avg_buy=row[9]
    avg_sell=row[10]
    avg_amount=row[11]
    # 省略
    param={
        "timestamp":timestamp,
        "open":open,
        "high":high,
        "low":low,
        "close":close,
        "volume":vol,
        "vol_buy":vol_buy,
        "vol_sell":vol_sell,
        "avg_buy":avg_buy,
        "avg_sell":avg_sell,
        "avg_amount":avg_amount
    }
    for cntback in [1,2,3,4,5,6,7,8,9,10,12,15,20,25,30,35,40,50]:
        key_name='vol_diff'+str(cntback)
        param[key_name]=0
        for cnt2 in (0,cntback):
            param[key_name]+=rows[cnt1-cntback][7]
            param[key_name]-=rows[cnt1-cntback][8]
    sqls.append(param)


mypgmanager.execute_many(
        'insert into '+ tablename +'_with_vol_diffs(timestamp,o,h,l,c,vol,vol_buy,vol_sell,avg_buy,avg_sell,avg_amount_per_trade,vol_diff1,vol_diff2,vol_diff3,vol_diff4,vol_diff5,vol_diff6,vol_diff7,vol_diff8,vol_diff9,vol_diff10,vol_diff12,vol_diff15,vol_diff20,vol_diff25,vol_diff30,vol_diff35,vol_diff40,vol_diff50) values'
                                     '(%(timestamp)s,%(open)s,%(high)s,%(low)s,'
                                     '%(close)s,%(volume)s,%(vol_buy)s,%(vol_sell)s,'
                                     '%(avg_buy)s,%(avg_sell)s,%(avg_amount)s,'
                                     '%(vol_diff1)s,%(vol_diff2)s,%(vol_diff3)s,'
                                     '%(vol_diff4)s,%(vol_diff5)s,%(vol_diff6)s,'
                                     '%(vol_diff7)s,%(vol_diff8)s,%(vol_diff9)s,'
                                     '%(vol_diff10)s,%(vol_diff12)s,%(vol_diff15)s,'
                                     '%(vol_diff20)s,%(vol_diff25)s,%(vol_diff30)s,'
                                     '%(vol_diff35)s,%(vol_diff40)s,%(vol_diff50)s)', sqls)
a=1
