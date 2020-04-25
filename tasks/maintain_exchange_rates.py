from packages import forex as FOREX
from packages import currency_pair as CP
from packages import db as DB
import CONSTANTS
import time

forex=FOREX.Forex('45452','91adb4e0e222cbdb9a55951ce00f8077','http://api.k780.com')
currency_pairs=[CP.CurrencyPair('MXN','USD'),CP.CurrencyPair('JPY','USD')]
starting_timestamp=1564588800
current_timestamp=starting_timestamp
ending_timestamp=1568995200

pgmanager=DB.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)

while current_timestamp<ending_timestamp:
    for cp in currency_pairs:
        rate=forex.rate(cp.base,cp.reference,current_timestamp)
        print(current_timestamp,'  :  ',rate)
        dict={
            'base':cp.base,
            'reference':cp.reference,
            'rate':rate,
            'timestamp':current_timestamp
        }
        sql='insert into exchange_rates(base,reference,rate,timestamp) values(\'%(base)s\',\'%(reference)s\',\'%(rate)s\',\'%(timestamp)s\')'%dict
        pgmanager.execute(sql)
        time.sleep(72)
        current_timestamp+=86400


