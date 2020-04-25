# -*- coding: UTF-8 -*-
import csv
from packages import universal
from packages import okex


def get_key_pair(discription="test"):
    f=open('API_list.csv','r')
    reader=csv.reader(f)
    result=[]
    for row in reader:
        if row[9]==discription:
            result= [row[7],row[8],row[3]]
    f.close()
    return result

class Account:
    # def __init__(self, description="test"):
    #     key_pair=get_key_pair(description)
    #     self.api_key=key_pair[0]
    #     self.secret_key=key_pair[1]
    #     self.description=description
    #     self.name=key_pair[2]

    def __init__(self, api_key, secret_key, name='test', description='test'):
        self.api_key=api_key
        self.secret_key=secret_key
        self.name=name
        self.description=description


    def set_balance(self, balance_info=None):
        if balance_info.__class__!= universal.BalanceInfo:
            okex1= okex.OKEx(self)
            balance_info=okex1.balances()
        self.balance_info=balance_info  # universal.BalanceInfo class

    def set_orders(self, orders):
        self.orders=orders

    def get_rough_equivalent_asset(self, reference= 'usdt'):
        self.set_balance()
        free=self.balance_info.free
        frozen=self.balance_info.frozen
        total_asset={}
        equivalent_asset=0
        for coin in free:
            total_asset[coin]=float(free[coin])
        for coin in frozen:
            total_asset[coin]+=float(frozen[coin])
        try:
            for coin in total_asset:
                okex1= okex.OKEx(self)
                if total_asset[coin]!=0:
                    if coin==reference:
                        ratio=1
                    else:
                        ratio=(okex1.ticker(coin + '_' + reference)).last
                        if ratio==0:
                            ratio=1/(okex1.ticker(reference + '_' + coin)).last
                    equivalent_asset+=total_asset[coin]*ratio
        except:
            pass
        self.equivalent_asset=equivalent_asset
        return equivalent_asset

    def change_coins(self):
        pass

    def set_position(self, positions={"btc":0.5,"ltc":0.5}):
        '''

        :param positions:
        :return:
        '''
        key1,key2=positions.keys()
        holdings={}
        self.positions=positions
        return
        self.set_balance()
        for coin_name in self.balance_info.free:
            if coin_name==key1:
                holdings[key1]=self.balance_info.free[coin_name]
            if coin_name==key2:
                holdings[key2]=self.balance_info.free[coin_name]
        for coin_name in self.balance_info.frozen:
            if coin_name==key1:
                holdings[key1]+=self.balance_info.frozen[coin_name]
            if coin_name==key2:
                holdings[key2]+=self.balance_info.frozen[coin_name]

    def set_initial_positions(self, positions):
        '''

        :param positions: a dict like {
            'btc':123,
            'usdt':456
        }
        :return:
        '''
        self.initial_positions=positions
