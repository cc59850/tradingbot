import numpy as np
from packages import db as DB
import CONSTANTS
import json

def normalize(data, method='max'):
    _range=np.max(abs(data))
    if _range==0:
        return data+0.0000001
    else:
        return data/_range

def read_data(market='KrakenRest', starting_timestamp=1567267200, duration=86400, forcasting_period=300, sample_number=1000):
    pgmanager=DB.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)
    ending_timestamp=starting_timestamp+duration
    # 取出depths的数据
    sql='select * from depths where market=\'' + market + '\' and timestamp between ' + str(starting_timestamp) + ' and ' + str(ending_timestamp) + ' order by timestamp'
    rows=pgmanager.select(sql)
    depths=[]
    askss=[]
    bidss=[]
    supports=[]
    resistances=[]

    # 取出trades的数据
    ending_timestamp=ending_timestamp+forcasting_period
    sql2='select * from trades where market=\'Kraken\' and timestamp between ' + str(starting_timestamp) + ' and ' + str(ending_timestamp) + ' order by timestamp'
    rows2=pgmanager.select(sql2)

    # 对逐笔数据进行处理
    for row in rows:
        timestamp=row[2]
        support=99999999
        resistance=-99999999
        # iterate over rows2 to determine the high and low
        for cnt in range(0,len(rows2)):
            row2=rows2[cnt]
            timestamp_for_rows2=row2[3]
            if timestamp_for_rows2>timestamp and timestamp_for_rows2<=timestamp+forcasting_period:
                price=row2[5]
                if price<support:
                    support=price
                if price>resistance:
                    resistance=price
            if timestamp_for_rows2>timestamp+forcasting_period:
                break

        d=json.loads(row[3])
        asks=d['asks']
        bids=d['bids']
        askss.append(asks)
        bidss.append(bids)
        supports.append(support)
        resistances.append(resistance)
    askss=np.array(askss)
    bidss=np.array(bidss)
    resistances=np.array(resistances)
    supports=np.array(supports)
    return {
        'bidss':bidss,
        'askss':askss,
        'supports':supports,
        'resistances':resistances
    }
