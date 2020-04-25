import time
import requests
import json
from packages import liquid as LIQUID
from packages import kraken as KRAKEN
from packages import account as ACCOUNT
from packages import currency_pair as CURRENCYPAIR
from packages import universal as UNIVERSAL

# pgmanager
from packages import db as DB
import CONSTANTS
pgmanager=DB.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)
currency_pair=CURRENCYPAIR.CurrencyPair()

def get_rows(sql):
    return pgmanager.select(sql)

def combine_trades_by_timestamp(rows):
    trades=[]
    current_timestamp=rows[0][3]
    current_price=rows[0][5]
    current_amount=rows[0][6]
    current_trade_type=rows[0][4]
    rows_len=len(rows)
    cnt=1
    trade=UNIVERSAL.TradeInfo(current_timestamp,current_price,current_amount,current_trade_type)

    while cnt<rows_len:
        row=rows[cnt]
        timestamp = row[3]
        price = row[5]
        amount = row[6]
        trade_type = row[4]
        if current_timestamp==timestamp:
            if current_trade_type==trade_type:
                if current_price==price:
                    # 时间、方向、价格都相同，认为是同一笔交易
                    trade.amount+=amount
                else:
                    # 时间、类型相同，价格不同，不是同一笔交易
                    trades.append(trade)
                    current_timestamp = timestamp
                    current_price = price
                    current_amount = amount
                    current_trade_type = trade_type
                    trade = UNIVERSAL.TradeInfo(current_timestamp, current_price, current_amount, current_trade_type)
            else:
                # 时间相同，类型不同，认为是不同交易
                trades.append(trade)
                current_timestamp = timestamp
                current_price = price
                current_amount = amount
                current_trade_type = trade_type
                trade = UNIVERSAL.TradeInfo(current_timestamp, current_price, current_amount, current_trade_type)
        else:
            # 时间戳不同，不是同一笔交易
            trades.append(trade)
            current_timestamp = timestamp
            current_price = price
            current_amount = amount
            current_trade_type = trade_type
            trade = UNIVERSAL.TradeInfo(current_timestamp, current_price, current_amount, current_trade_type)
        cnt+=1
    _trades=UNIVERSAL.Trades('Kraken',currency_pair,None)
    _trades.trades=trades
    return _trades

rows=get_rows('select * from trades_for_kraken order by timestamp')
trades=combine_trades_by_timestamp(rows)
sqls=[]
for trade in trades.trades:
    param = {
        'timestamp': int(trade.timestamp),
        'tid': trade.tid,
        'price': trade.price,
        'amount': trade.amount,
        'trade_type': trade.trade_type,
        'status': trade.status,
        'order_type': 'm',
        'market': 'Kraken'
    }
    sqls.append(param)

pgmanager.execute_many(
    "insert into trades_cleansed_for_kraken(timestamp,tid,price,amount,trade_type,status,order_type,market) values(%(timestamp)s,%(tid)s,%(price)s,%(amount)s,%(trade_type)s,%(status)s,%(order_type)s,%(market)s)",
    sqls)


