from packages import db as DB
import CONSTANTS
pgmanager=DB.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)

# 查询所有tid重复的记录
sql='select * from trades where (tid) in (select tid from trades group by tid having count(*) > 1) order by tid '
rows=pgmanager.select(sql)
print('总共有',len(rows),'行数据')
previous_tid='0000'
cnt=0
sqls=[]
for row in rows:
    # 整体思想是对含有current_tid的行进行计数，如果计数>=2，则删除此行，否则不做操作
    if previous_tid==row[2]:
        # 本次的tid和上次的相同，根据id删除本次的行
        param = {
            'id': row[0],
        }
        sqls.append(param)
        cnt+=1
        if cnt%1000==0:
            pgmanager.execute_many('delete from trades where id=%(id)s',sqls)
            sqls=[]
            print('已经处理了',cnt,'行')
        if cnt==len(rows)/2:
            pgmanager.execute_many('delete from trades where id=%(id)s', sqls)
            sqls = []
            print('已经处理了', cnt, '行')
    else:
        # 本次的tid和上次的不相同，不做处理
        previous_tid=row[2]
pgmanager.execute_many('delete from trades where id=%(id)s',sqls)
sqls=[]
print('已经处理了',cnt,'行')