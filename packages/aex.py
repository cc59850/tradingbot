# -*- coding: UTF-8 -*-
import sys
sys.path.append("..")
from packages import universal
import time
from packages import exchange as EXCHANGE
import requests
from packages import error_code as ERRORCODE
import json

# 根据 CurrencyPair 实例构造一个request的字符串
def make_currency_pair_string(currency_pair):
    base = AEX.COINNAMEMAPPING.get(currency_pair.base, currency_pair.base)
    reference = AEX.COINNAMEMAPPING.get(currency_pair.reference, currency_pair.reference)
    return 'c=' + base + '&mk_type=' + reference

class Aex(EXCHANGE.Exchange):

    MARKET = 'AEX'
    COINNAMEMAPPING={
        'cny':'cnc',
    }


    def __init__(self,account, user_id, base_url=None):
        self.account = account
        self.user_id=str(user_id)
        if not base_url is None:
            self.base_url = base_url
        else:
            self.base_url=EXCHANGE.Exchange.MARKET_BASEURL_MAPPING['AEX']

    def ticker(self, currency_pair, aggregational=False):
        # /ticker.php?c=all&mk_type=cnc
        TICKER_RESOURCE = "/ticker.php"
        params = make_currency_pair_string(currency_pair)
        result=requests.get(self.base_url+TICKER_RESOURCE,params)
        if result.status_code!=200:
            return ERRORCODE.Error_Code_For_Status_Code[result.status_code]
        if aggregational==True:
            result=json.loads(result.text)
        else:
            result = universal.Ticker(self.MARKET, currency_pair, result.text)
        return result

    def depth(self,currency_pair, raw=False):
        # https://api.aex.zone/depth.php?c=btc&mk_type=cnc
        DEPTH_RESOURCE = "/depth.php"
        params = make_currency_pair_string(currency_pair)
        result = requests.get(self.base_url+DEPTH_RESOURCE,params)
        if result.status_code!=200:
            return ERRORCODE.Error_Code_For_Status_Code[result.status_code]
        if raw == True:
            return result.text
        else:
            result = universal.Depth(self.MARKET, currency_pair, result.text)
            return result

    def trades(self, currency_pair, tid=None, raw=False):
        # https://api.aex.zone/trades.php?c=btc&mk_type=cnc
        TRADES_RESOURCE = "/trades.php"
        params = make_currency_pair_string(currency_pair)
        if not tid is None:
            params+='&tid='+str(tid)
        result = requests.get(self.base_url + TRADES_RESOURCE, params)
        if result.status_code!=200:
            return ERRORCODE.Error_Code_For_Status_Code[result.status_code]
        if raw == True:
            return result.text
        else:
            result = universal.Trades(self.MARKET, currency_pair, result.text,2,self.user_id)
            return result

    def balances(self):
        # https://api.aex.zone/getMyBalance.php
        from packages import util
        aex2=util.Client(self.account.api_key,self.account.secret_key,self.user_id)
        result=aex2.getMyBalance()
        result=universal.BalanceInfo(self.MARKET,result)
        return result

    def submit_order(self, type, currency_pair, price, amount):
        from packages import util
        aex2 = util.Client(self.account.api_key, self.account.secret_key, self.user_id)
        result = aex2.submitOrder(type,currency_pair.reference,price,amount,currency_pair.base)
        type="buy" if type==1 else "sell"
        result = universal.OrderInfo(self.MARKET, currency_pair, result, {'price':price,'amount':amount,'type':type})
        return result

    def cancel_order(self,currency_pair,order_id):
        from packages import util
        aex2 = util.Client(self.account.api_key, self.account.secret_key, self.user_id)
        result = aex2.cancelOrder(currency_pair.reference,order_id,currency_pair.base)
        result = universal.CancelOrderResult(self.MARKET,currency_pair,result,order_id)
        return result

    def order_list(self,currency_pair, current_page=1, page_length=200):
        from packages import util
        aex2 = util.Client(self.account.api_key, self.account.secret_key, self.user_id)
        result = aex2.getOrderList(currency_pair.base,currency_pair.reference)
        result=universal.SubmittedOrderList(currency_pair,self.MARKET,result)
        return result

    def trade_list(self,currency_pair, current_page=1, page_length=200):
        from packages import util
        aex2 = util.Client(self.account.api_key, self.account.secret_key, self.user_id)
        result = aex2.getMyTradeList(currency_pair.reference,currency_pair.base,current_page)
        result = universal.Trades(self.MARKET, currency_pair,result,2, self.user_id)
        return result