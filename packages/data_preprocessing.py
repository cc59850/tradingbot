# encoding=utf-8
import time

import matplotlib.pyplot as plt
import numpy as np
import math
import utils
import numpy as np
from packages import db as DB
import CONSTANTS
import json
import sqlite3
import csv

conn=None
cur=None

def load_exchange_rates():
    global conn,cur

    starting_timestamp=None
    ending_timestamp=None
    # 创建一个数据表，以备使用
    sql = 'CREATE TABLE processed_exchange_rates (id integer primary key AUTOINCREMENT,currency_pair varchar(16),timestamp integer, rate numeric)'
    cur.execute(sql)
    conn.commit()

    # 填充这个数据表
    rows=[]
    id = 0
    with open('G:\\量化交易\\USDJPY5.csv')as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            str_time=str(row[0])+' '+str(row[1])
            timestamp=int(time.mktime(time.strptime(str_time,'%Y.%m.%d %H:%M')))
            id+=1
            rows.append([id,'USDJPY',timestamp,row[5]])
    with open('G:\\量化交易\\USDMXN5.csv')as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            str_time = str(row[0]) + ' ' + str(row[1])
            timestamp = int(time.mktime(time.strptime(str_time, '%Y.%m.%d %H:%M')))
            id += 1
            rows.append([id, 'USDMXN', timestamp, row[5]])
    sql="insert into processed_exchange_rates values(?,?,?,?)"
    cur.executemany(sql, rows)
    conn.commit()

    # 对整个表按照时间戳进行插值
    # 得到所有的交易对
    sql='select distinct(currency_pair) from processed_exchange_rates'
    cur.execute(sql)
    rows=cur.fetchall()
    currency_pairs=[]
    for row in rows:
        currency_pairs.append(row[0])

    # 针对每个交易对进行插值处理
    for currency_pair in currency_pairs:
        sql='select * from processed_exchange_rates where currency_pair=\'%s\' order by timestamp'%(currency_pair)
        cur.execute(sql)
        rows_for_this_currency_pair=cur.fetchall()
        # 从最小的那个timestamp开始，每次加300，查询数据库中是否有该记录，如果有，不处理，如果没有：
        # 取出比这个timestamp略小的那个行记录和比这个timestamp略大的那个行记录对应的rate，按照线性进行插值
        sql='select min(timestamp) from processed_exchange_rates where currency_pair=\'%s\''%(currency_pair)
        cur.execute(sql)
        rows=cur.fetchall()
        starting_timestamp=rows[0][0]
        sql = 'select max(timestamp) from processed_exchange_rates where currency_pair=\'%s\'' % (currency_pair)
        cur.execute(sql)
        rows = cur.fetchall()
        ending_timestamp = rows[0][0]
        for timestamp in range(starting_timestamp,ending_timestamp+1,300):
            sql='select count(*) from processed_exchange_rates where currency_pair=\'%s\' and timestamp=\'%s\''%(currency_pair,timestamp)
            cur.execute(sql)
            rows=cur.fetchall()
            if rows[0][0]==0:
                # 取出比这个timestamp略小的那个行记录和比这个timestamp略大的那个行记录对应的rate，按照线性进行插值
                sql = 'select min(timestamp) from processed_exchange_rates where currency_pair=\'%s\' and timestamp>\'%s\'' % (currency_pair,timestamp)
                cur.execute(sql)
                rows = cur.fetchall()
                next_timestamp = rows[0][0]
                sql = 'select max(timestamp) from processed_exchange_rates where currency_pair=\'%s\' and timestamp<\'%s\'' % (currency_pair,timestamp)
                cur.execute(sql)
                rows = cur.fetchall()
                previous_timestamp = rows[0][0]
                sql='select rate from processed_exchange_rates where currency_pair=\'%s\' and timestamp=\'%s\'' % (currency_pair,previous_timestamp)
                cur.execute(sql)
                rows=cur.fetchall()
                rate0= float(rows[0][0])
                sql = 'select rate from processed_exchange_rates where currency_pair=\'%s\' and timestamp=\'%s\'' % (currency_pair, next_timestamp)
                cur.execute(sql)
                rows = cur.fetchall()
                rate1 = float(rows[0][0])
                estimated_rate=(rate1-rate0)/((next_timestamp-previous_timestamp)/300)+rate0
                sql='insert into processed_exchange_rates values(NULL,\'%s\',\'%s\',\'%s\')'%(currency_pair,timestamp,estimated_rate)
                cur.execute(sql)
                conn.commit()

def load_data_to_memory_database(starting_timestamp, ending_timestamp,forcasting_period):
    global conn,cur

    pgmanager = DB.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)
    # 记录时间
    t0 = time.time()
    sql = 'select * from depths where timestamp between ' + str(starting_timestamp) + ' and ' + str(ending_timestamp) + ' order by timestamp'
    rows_for_depths = pgmanager.select(sql)
    sql='select * from trades where timestamp between ' + str(starting_timestamp) + ' and ' + str(ending_timestamp+forcasting_period) + ' order by timestamp'
    rows_for_trades=pgmanager.select(sql)
    print(time.time() - t0)

    t1 = time.time()

    # 创建表
    sql = 'CREATE TABLE processed_depths (id integer primary key ,market varchar(64),timestamp integer, depth text )'
    cur.execute(sql)
    conn.commit()
    sql='CREATE TABLE processed_trades (id integer primary key ,market varchar(64),tid varchar(64),timestamp integer,  trade_type integer ,price numeric , amount numeric , status integer , order_type varchar(4))'
    cur.execute(sql)
    conn.commit()

    # 将psql的行写入内存数据库
    sql = "insert into processed_depths values(?,?,?,?)"
    cur.executemany(sql, rows_for_depths)
    conn.commit()
    sql='insert into processed_trades values(?,?,?,?,?,?,?,?,?)'
    cur.executemany(sql,rows_for_trades)
    conn.commit()
    print(time.time() - t1)

    # 测试查询
    sql='select min(price) from processed_trades where timestamp>1567267200 and timestamp<=1567267500'
    cur.execute(sql)
    rows=cur.fetchall()

    # 创建索引
    sql = 'CREATE INDEX index_timestamp_for_depths ON processed_depths (timestamp);'
    cur.execute(sql)
    conn.commit()
    sql='CREATE INDEX index_timestamp_for_trades ON processed_trades (timestamp);'
    cur.execute(sql)
    conn.commit()

def read_data(markets=[],starting_timestamp=1567267200, duration=86400, forcasting_period=2400, forcasting_amount=100, exchange_rates={}, sample_number=1000):
    '''
    这个模块实现的功能是：
    在指定的时间内取出对应的深度列表、支撑和阻力位
    :param markets:
    :param starting_timestamp:
    :param duration:
    :param forcasting_period:
    :param forcasting_amount:
    :param exchange_rates:
    :param sample_number:
    :return:
    '''
    global conn,cur
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()

    # 猜测的开始时间戳和结束时间戳
    ending_timestamp=starting_timestamp+duration

    # 读汇率
    load_exchange_rates()

    # 要返回的值
    depths = {}
    supports = []
    resistances = []

    pgmanager=DB.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)

    # 0. 将数据读入到内存数据库中
    load_data_to_memory_database(starting_timestamp,ending_timestamp,forcasting_period)

    # 1. 取出所有的交易市场，并将其映射到depths的键集合上
    sql = 'select distinct(market) from processed_depths'
    rows_for_all_markets = cur.execute(sql)

    for row in rows_for_all_markets:
        depths[row[0]] = []

    # 2. 先取出timestamp序列存入timestamps列表中
    cur.execute('select distinct(timestamp) from processed_depths order by timestamp')
    rows_for_timestamps = cur.fetchall()
    starting_timestamp=rows_for_timestamps[0][0]
    ending_timestamp=rows_for_timestamps[-1][0]

    # 3. 取出trades数据
    ending_timestamp2 = ending_timestamp + forcasting_period
    sql2 = 'select * from trades where market=\'Kraken\' and timestamp between ' + str(
        starting_timestamp) + ' and ' + str(ending_timestamp2) + ' order by timestamp'
    rows_for_trades = pgmanager.select(sql2)

    # # 3.1 取出exchange rates数据
    # sql1='select * from processed_exchange_rates where currency_pair=\'USDJPY\' and timestamp>='+str(starting_timestamp)+' and timestamp<='+str(ending_timestamp)+' order by timestamp'
    # sql2='select * from processed_exchange_rates where currency_pair=\'USDMXN\' and timestamp>='+str(starting_timestamp)+' and timestamp<='+str(ending_timestamp)+' order by timestamp'
    # cur.execute(sql1)
    # rows_for_rates_of_USDJPY=cur.fetchall()
    # cur.execute(sql2)
    # rows_for_rates_of_USDUSDMXN=cur.fetchall()

    # 4. 遍历timestamps列表中的所有timestamp，并分析processed_depths表和trades表中的数据
    # 此处需要修改current_timestamp为即将被迭代的那个timestamp
    t1=time.time()
    for row in rows_for_timestamps:
        current_timestamp=row[0]
        # 取出当前时间戳的depth数据
        sql='select * from processed_depths where timestamp='+str(current_timestamp)
        cur.execute(sql)
        rows_for_current_timestamp=cur.fetchall()
        # 一共大约16条数据，隶属于16个不同的交易市场，对每个单独的条目进行标准化，然后写入到一个列表中
        # 将此次查询的数据从list变为dict形式，方便后续索引
        temp_rows_for_current_timestamp={}
        for row in rows_for_current_timestamp:
            temp_rows_for_current_timestamp[row[1]]=json.loads(row[3])
        # 将此次查询的大约16条数据的depths数据中的bids和asks分别附加到depths的bids和asks中，注意Okex的asks要做一次reverse
        # 同时要注意异常时间戳，有时无法得到16家交易所的完整数据，此时，用一个默认的数据代替缺失数据
        # 默认的填充交易所：['Binance','Bittrex','Bitstamp','KrakenRest']
        default_markets=['Coinbase','Binance','Bittrex','Bitstamp','KrakenRest','Poloniex','Bitfinex']
        for market in default_markets:
            if temp_rows_for_current_timestamp.__contains__(market):
                asks = temp_rows_for_current_timestamp[market]['asks']
                bids = temp_rows_for_current_timestamp[market]['bids']
                break
        default_depth={
            'asks':asks,
            'bids':bids
        }
        # 将抽离出来的bids和asks数据写入到对应的键值对的bids、asks的序列中
        for key in depths.keys():
            if temp_rows_for_current_timestamp.__contains__(key):
                depth=temp_rows_for_current_timestamp[key]
                if key == 'Okex':
                    depth['asks'].reverse()
                if key == 'Bitstamp':
                    depth['asks']=depth['asks'][:200]
                    depth['bids']=depth['bids'][:200]
                if key == 'Liquid':
                    # 因为liquid交易所只有BTC-JPY交易的，所以要对JPY定价的BYC进行换权处理，变成USD定价
                    # 而又因为每时每刻的JPY-USD定价都在变动，所以选取MT4上面的历史数据作为JPY-USD定价标准
                    sql='select rate from processed_exchange_rates where currency_pair=\'USDJPY\' and timestamp=(select max(timestamp) from processed_exchange_rates where timestamp<%s)'%(current_timestamp)
                    cur.execute(sql)
                    rows=cur.fetchall()
                    rate=rows[0][0]
                    for bid in depth['bids']:
                        bid[0]=bid[0]/rate
                    for ask in depth['asks']:
                        ask[0]=ask[0]/rate
                    a=1

                if key == 'Bitso':
                    # 同上面的，这次先取得墨西哥比索-美元的定价，在进行换权处理
                    sql = 'select rate from processed_exchange_rates where currency_pair=\'USDMXN\' and timestamp=(select max(timestamp) from processed_exchange_rates where timestamp<%s)' % (
                        current_timestamp)
                    cur.execute(sql)
                    rows = cur.fetchall()
                    rate = rows[0][0]
                    for bid in depth['bids']:
                        bid[0] = bid[0] / rate
                    for ask in depth['asks']:
                        ask[0] = ask[0] / rate
                    a = 1
            else:
                depth=default_depth
            depths[key].append(depth)

        # 计算trades中未来n秒所触及到的高点和低点
        # 取出阻力点位
        sql='select max(price) from processed_trades where timestamp>'+ str(current_timestamp) +' and timestamp<='+str(current_timestamp + forcasting_period)
        cur.execute(sql)
        rows=cur.fetchall()
        resistance=rows[0][0]
        # 取出支撑点位
        sql = 'select min(price) from processed_trades where timestamp>' + str(
            current_timestamp) + ' and timestamp<=' + str(current_timestamp + forcasting_period)
        cur.execute(sql)
        rows = cur.fetchall()
        support = rows[0][0]
        supports.append(support)
        resistances.append(resistance)
    print('一共用了',time.time()-t1,'秒，完成了',len(rows_for_timestamps),'次大迭代')

    conn.close()
    return {
        'depths':depths,
        'supports': supports,
        'resistances': resistances
    }

def get_resistances_and_supports(rows_for_timestamps, accumulated_volume=100, buying_volume=None, selling_volume=None):
    '''
    # 计算trades中未来n秒所触及到的高点和低点
    :return:
    '''
    global conn, cur
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()

    resistances=[]
    supports=[]
    starting_timestamp = rows_for_timestamps[0][0]
    ending_timestamp = rows_for_timestamps[-1][0]



    for row in rows_for_timestamps:
        current_timestamp = row[0]
        # 一直向后搜索，求得双向成交量，
        # 从这条时间戳向后数，当量累计到 accumulateed_volume 时，取出这所有交易里面的最高点和最低点
        sql = 'select * from processed_trades where timestamp>' + str(current_timestamp) + ' and timestamp<=' + str(current_timestamp+3600)
        cur.execute(sql)
        rows_for_all_trades = cur.fetchall()

    pass
if __name__=='__main__':
    # 生成数据
    # 除了按等时间间隔生成数据，还可以按照等成交量生成数据，还可以按照等买卖量
    import pickle
    starting_ts = 1567267200
    for ts in range(starting_ts, starting_ts + 86400*10+ 1, 86400):
        t0 = time.time()
        data = read_data(starting_timestamp=ts, duration=86400, forcasting_period=60)
        file = open('data'+'_'+str(ts)+'_60s', 'wb')
        pickle.dump(data, file)
        file.close()
        print('处理数据用时：', time.time() - t0)
