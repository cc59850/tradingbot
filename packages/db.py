# -*- coding: UTF-8 -*-
import sys

# 基于 sqlite4dummy 的基本架构重新写了一个超简易版本的 sqlite 数据库管理库
# 本程序提供必要的sqlite操作方法，并对一个sqlite数据库进行初始化
# 本程序从自己启动，外部只能调用其方法
# 本程序的主入口程序为 main()

# 请填写下面几个参数：
# 第一个参数为数据库名称
DB_NAME=''


import os
import sqlite3
import psycopg2

class PGManager():
    def __init__(self, database='', user='', pw='', host='', port=''):
        self.conn_args={'database':database, 'user':user, 'password':pw, 'host':host, 'port':port}

    def execute(self,sql):
        try:
            self.conn = psycopg2.connect(**self.conn_args)
            cursor=self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def select(self, sql):
        try:
            rows=[]
            self.conn = psycopg2.connect(**self.conn_args)
            cursor = self.conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
        except Exception as e:
            print(e)
            rows=[]
        finally:
            self.conn.close()
            return rows

    def execute_many(self,query, sql_sequence):
        try:
            self.conn = psycopg2.connect(**self.conn_args)
            cursor=self.conn.cursor()
            cursor.executemany(query, sql_sequence)
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def close(self):
        self.conn.close()


if __name__=='__main__':
    pass