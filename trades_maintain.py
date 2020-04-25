import sys
sys.path.append('../')
import time
from packages import binance as BINANCE
from packages import account as ACCOUNT
from packages import currency_pair as CURRENCYPAIR

# pgmanager
from packages import db as DB
import CONSTANTS
pgmanager=DB.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)

account=ACCOUNT.Account('gBAyXDQx4SWJ1FKI5cG4xaYJVwTNnMWUVcrvHjNVAKjxmt0JrpLpowQ85Kg49Ak9','EZaHgc67HCNeniUGiLbTBHZJyYsq5MyVPuwOugXUSeTz1mKma1wWaPm3yTeAN7En')
binance=BINANCE.Binance(account)
# liquid=LIQUID.Liquid(account)
# kraken=KRAKEN.Kraken(account)
exchange=binance

currency_pair=CURRENCYPAIR.CurrencyPair('btc','usdt')

def digest_data(interval=86400, market='Kraken'):
    _name_map='XXBT'+'Z'+currency_pair.reference.upper()
    # table_name = 'trades_' + currency_pair.base + '_' + currency_pair.reference + '_kraken'
    table_name = 'trades_for_binance'
    # select * from trades_for_binance where tid=(select max(tid) from trades_for_binance)
    sql='select * from '+table_name +' where tid=(select max(tid) from ' + table_name +') '
    rows=pgmanager.select(sql)
    if len(rows)==0:
        starting_timestamp=int(1546272000)
        starting_id=100000000
    else:
        starting_timestamp=int(rows[0][3])
        starting_id=int(rows[0][2])+1
    if interval==0:
        ending_timestamp=int(time.time())
    else:
        ending_timestamp=int(starting_timestamp+interval)
    trades=[]
    cnt=0
    while starting_timestamp<ending_timestamp-1000:
        _trades=exchange.trades(currency_pair,since=starting_id,raw=False)
        # symbol=KRAKEN.make_currency_pair_string_for_restful(currency_pair)
        # try:
        #     pass
        #     _trades=json.loads(_trades)
        # except:
        #     time.sleep(60)
        #     continue
        # _trades=_trades['result'][_name_map]

        # _trades=sorted(_trades, key=lambda x:x['timestamp'])
        if len(_trades.trades)==0:
            continue
        _trades=_trades.trades
        # _trades.reverse()
        trades.extend(_trades)
        starting_timestamp=(int(_trades[-1].timestamp)/1000)
        starting_id=_trades[-1].tid+1
        local_time = time.gmtime(starting_timestamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        print(str(otherStyleTime))
        cnt+=1
        time.sleep(1.5)

    sqls=[]
    for trade in trades:
        param={
            'timestamp':int(trade.timestamp),
            'tid':trade.tid,
            'price':trade.price,
            'amount':trade.amount,
            'trade_type':trade.trade_type,
            'status':trade.status,
            'order_type':'m',
            'market':'binance'
        }
        sqls.append(param)

    pgmanager.execute_many(
        "insert into " + table_name + "(timestamp,tid,price,amount,trade_type,status,order_type,market) values(%(timestamp)s,%(tid)s,%(price)s,%(amount)s,%(trade_type)s,%(status)s,%(order_type)s,%(market)s)",sqls)

for cnt in range(500):
    digest_data(interval=86400)