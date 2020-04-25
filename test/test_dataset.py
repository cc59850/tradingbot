import sqlite3
from packages import db as DB
import CONSTANTS
import time

pgmanager=DB.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)
# 记录时间
t0=time.time()
sql = 'select * from depths where timestamp between 1567267200 and 1567353909 order by timestamp'
rows_for_depths = pgmanager.select(sql)
print(time.time()-t0)

# 测试插入
t1=time.time()
conn=sqlite3.connect(':memory:')
cur = conn.cursor()
# 创建表
sql='CREATE TABLE processed_depths (id integer primary key ,market varchar(64),timestamp integer, depth text )'
cur.execute(sql)
conn.commit()

sql="insert into processed_depths values(? ,?,?,?)"
cur.executemany(sql,rows_for_depths)
conn.commit()
print(time.time()-t1)

# 创建索引
sql='CREATE INDEX index_timestamp ON processed_depths (timestamp);'
cur.execute(sql)
conn.commit()

# 测试select
t2=time.time()
cur.execute('select distinct(timestamp) from processed_depths order by timestamp')
rows=cur.fetchall()
print(time.time()-t2)

# 测试select2
t2=time.time()
for row in rows:
    timestamp=row[0]
    cur.execute('select * from processed_depths where timestamp=' + str(timestamp))
    result=cur.fetchall()
    if len(result)!=16:
        print('At '+str(timestamp)+' , threr are '+str(len(result))+' items!')

print(time.time()-t2)
a=1


