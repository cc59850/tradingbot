# -*- coding: UTF-8 -*-
import sys
sys.path.append("..")
import json
import time
import requests
import copy

from websocket import create_connection

from packages import error_code as ERRORCODE
from packages import exchange as EXCHANGE
from packages import universal
from packages.kraken_rest import api as KRAKEN_RAW_API

# 根据 CurrencyPair 实例构造一个request的字符串
def make_currency_pair_string(currency_pair):
    # base = AEX.COINNAMEMAPPING.get(currency_pair.base, currency_pair.base)
    # reference = AEX.COINNAMEMAPPING.get(currency_pair.reference, currency_pair.reference)
    result=Kraken.COINNAMEMAPPING.get(currency_pair.base,currency_pair.base) +'/' + Kraken.COINNAMEMAPPING.get(currency_pair.reference,currency_pair.reference)
    return result

def make_currency_pair_string_for_restful(currency_pair):
    # XXBTZUSD
    result = 'pair=' + Kraken.COINNAMEMAPPING.get(currency_pair.base, currency_pair.base) + Kraken.COINNAMEMAPPING.get(
        currency_pair.reference, currency_pair.reference)
    return result
def append_api_key(params, api_key):
    return params+'&apiKey=' + api_key
def sign(account, params):
    import hashlib
    import copy
    params['apiKey'] = account.api_key
    _params=copy.deepcopy(params)
    m = hashlib.md5()
    # params = {'symbol': 'usdt_btc', 'type': 'kline_1m', 'timestamp': TimeStampNow, 'apiKey': APIKEY, 'apiSecret': APISECRET}
    _params['apiSecrect']=account.secret_key
    _params['apiKey']=account.api_key
    keys = sorted(_params.keys())
    string = ''
    for key in keys:
        string = string + str(_params[key])
    m.update(string.encode(encoding='UTF-8'))
    encodestr = m.hexdigest()
    return encodestr

class Kraken(EXCHANGE.Exchange):

    MARKET = 'Kraken'
    COINNAMEMAPPING={
        'cny':'cnc',
        'btc':'XBT',
        'usdt':'USD'
    }

    def __init__(self,account, base_url=None):
        self.account = account
        if not base_url is None:
            self.base_url = base_url
        else:
            self.base_url=EXCHANGE.Exchange.MARKET_BASEURL_MAPPING['Kraken']
            self.base_url_for_rest='https://api.kraken.com'
        self.is_depth_subscribed=False
        self.initialize_ws()

    def initialize_ws(self):
        for i in range(3):
            try:
                # wscat -c wss://ws.kraken.com/
                self.ws = create_connection(self.base_url)
                print('web socket connection has established!')
                self.is_depth_subscribed=False
                self.is_trades_subscribed=False
                self._on_reading_message_flag = False
            except Exception as error:
                print('Caught this errr: ' + repr(error))
                time.sleep(3)
            else:
                break


    def _create_depth_link(self, currency_pair, limit=10):
        self._depth = universal.Depth('Kraken', currency_pair)
        self.api_update_book={"bid":{}, "ask":{}}
        pair=make_currency_pair_string(currency_pair)
        self.ws.send(json.dumps({
            "event": "subscribe",
            # "event": "ping",
            "pair": [pair],
            # "subscription": {"name": "ticker"}
            # "subscription": {"name": "spread"}
            # "subscription": {"name": "trade"},
            "subscription": {"name": "book", "depth": limit}
            # "subscription": {"name": "ohlc", "interval": 5}
        }))
        print('subscription for depth has been sent!')
        self.is_depth_subscribed=True
        if self._on_reading_message_flag==False:
            self._on_reading_message(currency_pair)

    def _create_trades_link(self, currency_pair):
        self._trades = universal.Trades('Kraken', currency_pair, [], 2)
        pair = make_currency_pair_string(currency_pair)
        self.ws.send(json.dumps({
            "event": "subscribe",
            # "event": "ping",
            "pair": [pair],
            # "subscription": {"name": "ticker"}
            # "subscription": {"name": "spread"}
            "subscription": {"name": "trade"},
            # "subscription": {"name": "book", "depth": limit}
            # "subscription": {"name": "ohlc", "interval": 5}
        }))
        print('subscription for trades has been sent!')
        self.is_trades_subscribed = True
        if self._on_reading_message_flag==False:
            self._on_reading_message(currency_pair)


    def _on_reading_message(self,currency_pair):
        self.responses_for_depth=[]
        self.responses_for_trades=[]
        self._on_reading_message_flag=True

        while True:
            try:
                result = self.ws.recv()
                _result=json.loads(result)
                if isinstance(_result,list) and len(_result)>3 and  str(_result[-2]).find('book-')!=-1:
                    self.responses_for_depth.append(result)
                    api_data = _result
                    if type(api_data) == list:
                        if "as" in api_data[1]:
                            self.api_update_book = universal.api_update_book(self.api_update_book, "ask",
                                                                             api_data[1]["as"])
                            self.api_update_book = universal.api_update_book(self.api_update_book, "bid",
                                                                             api_data[1]["bs"])
                        # signal.alarm(1)
                        elif "a" in api_data[1] or "b" in api_data[1]:
                            for x in api_data[1:len(api_data[1:]) - 1]:
                                if "a" in x:
                                    self.api_update_book = universal.api_update_book(self.api_update_book,"ask", x["a"])
                                elif "b" in x:
                                    self.api_update_book = universal.api_update_book(self.api_update_book,"bid", x["b"])
                    continue
                if isinstance(_result,list) and len(_result)>3 and  _result[-2]=='trade':

                    self.responses_for_trades.append(result)
                    continue
            except Exception as error:
                print('Caught this error: ' + repr(error))
                time.sleep(3)

    def get_currency_pairs_info(self):
        # GET https://openapi.digifinex.vip/v2/trade_pairs?apiKey=59328e10e296a&timestamp=1410431266&sign=0a8d39b515fd8f3f8b848a4c459884c2
        INFO_RESOURCE='/v2/trade_pairs'
        params = {}
        params['timestamp'] = str(time.time())
        params['sign'] = sign(self.account, params)
        result = requests.get(self.base_url + INFO_RESOURCE, params)
        result = universal.CurrencyPairInfos(self.MARKET, result.text)
        return result

    def ticker(self, currency_pair=None):
        # https://openapi.digifinex.vip/v2/ticker?apiKey=15d12cfa0a69be
        # https://openapi.digifinex.vip/v2/ticker?symbol=usdt_btc&apiKey=15d12cfa0a69be
        TICKER_RESOURCE = "/v2/ticker"
        if currency_pair is None:
            params='apiKey=' + self.account.api_key
            result = requests.get(self.base_url + TICKER_RESOURCE, params)
            if result.status_code != 200:
                return ERRORCODE.Error_Code_For_Status_Code[result.status_code]
            result = json.loads(result.text)
            code = result['code']
            if code != 0:
                return ERRORCODE.Error_code_for_DigiFinex[code]  # 这里要重新写
            result = result['ticker']
            return result
        else:
            params ='symbol=' + make_currency_pair_string(currency_pair)
            params=append_api_key(params,self.account.api_key)
            result=requests.get(self.base_url+TICKER_RESOURCE,params)
            if result.status_code!=200:
                return ERRORCODE.Error_Code_For_Status_Code[result.status_code]
            result=json.loads(result.text)
            code=result['code']
            if code!=0:
                return ERRORCODE.Error_code_for_DigiFinex[code]  #这里要重新写
            # result=result['ticker'][make_currency_pair_string(currency_pair)]
            result = universal.Ticker(self.MARKET, currency_pair, result)
            return result

    def depth(self,currency_pair, limit=10, raw=False):
        # v2: https://openapi.digifinex.vip/v2/depth?symbol=usdt_btc&apiKey=59328e10e296a&timestamp=1410431266&sign=0a8d39b515fd8f3f8b848a4c459884c2
        # v3：https://openapi.digifinex.com/v3/order_book?market=btc_usdt&limit=30
        '''

        :param currency_pair:
        :param raw:
        :return:
        '''
        # there are 4 required params: symbol, apikey, timestamp, sign
        import threading
        while True:
            if self.is_depth_subscribed==False:
                thread=threading.Thread(target=self._create_depth_link,args=(currency_pair,limit))
                thread.start()
                time.sleep(2)
            else:
                self._depth=universal.Depth(self.MARKET,currency_pair,self.api_update_book)
                return self._depth

    def trades(self, currency_pair, limit=1000, since=None, raw=False, order_type=None):
        # https://api.kraken.com/0/public/Trades?pair=XXBTZUSD
        TRADES_RESOURCE = "/0/public/Trades"
        params = make_currency_pair_string_for_restful(currency_pair)
        if since:
            params+='&since='+str(since)
        else:
            pass
        result=None
        while result is None:
            try:
                result = requests.get(self.base_url_for_rest + TRADES_RESOURCE, params,timeout=10)
            except:
                time.sleep(10)
                result=None
        if result.status_code!=200:
            return ERRORCODE.Error_Code_For_Status_Code[result.status_code]
        if raw == True:
            return result.text
        else:
            result = universal.Trades(self.MARKET, currency_pair, result.text,2,None,order_type)
            return result

    def balances(self):
        k = KRAKEN_RAW_API.API(key=self.account.api_key,secret=self.account.secret_key)
        result=k.query_private('Balance')
        return universal.BalanceInfo(self.MARKET,result)

    def submit_order(self, type, currency_pair, price, amount):
        k = KRAKEN_RAW_API.API(key=self.account.api_key, secret=self.account.secret_key)
        pair_name='X'+Kraken.COINNAMEMAPPING.get(currency_pair.base, currency_pair.base) + 'Z' + Kraken.COINNAMEMAPPING.get(
        currency_pair.reference, currency_pair.reference)
        action='buy' if type>=1 or type=='1' or type=='buy' else 'sell'
        result = k.query_private('AddOrder',
                                        {'pair': pair_name,
                                         'type': action,
                                         'ordertype': 'limit',
                                         'price': str(price),
                                         'volume': str(amount)
                                         })
        result = universal.OrderInfo(self.MARKET, currency_pair, result, {'price':price,'amount':amount,'type':type})
        return result

    def cancel_order(self,currency_pair,order_id):
        k = KRAKEN_RAW_API.API(key=self.account.api_key, secret=self.account.secret_key)

        result = k.query_private('CancelOrder',{'txid': order_id})
        result = universal.CancelOrderResult(self.MARKET, currency_pair, result, order_id)
        return result


    def trades_volume(self):
        # https: // api.kraken.com / 0 / private / TradeVolume
        k = KRAKEN_RAW_API.API(key=self.account.api_key, secret=self.account.secret_key)
        result = k.query_private('TradeVolume')
        return float(result['result']['volume'])

    def get_currency_pairs_info(self):
        # https://api.kraken.com/0/public/AssetPairs
        k = KRAKEN_RAW_API.API(key=self.account.api_key, secret=self.account.secret_key)
        result = k.query_public('AssetPairs')
        result = universal.CurrencyPairInfos(self.MARKET, result)
        return result

    @classmethod
    def get_fees(self, volume):
        volumes={
            'taker':[0,50000,100000,250000,500000,1000000,2500000,5000000,10000000,10**20],
            'maker':[0,50000,100000,250000,500000,1000000,2500000,5000000,10000000,10**20]
        }
        fee_multifliers={
            'taker': [0.26,0.24,0.22,0.2,0.18,0.16,0.14,0.12,0.1],
            'maker': [0.16,0.14,0.12,0.1,0.08,0.06,0.04,0.02,0]
        }
        fees={
            'maker':0.16,
            'taker':0.26
        }
        for cnt in range(0,len(volumes['taker'])):
            if volume<volumes['taker'][cnt]:
                fees['taker']=fee_multifliers['taker'][cnt-1]
                break
        for cnt in range(0,len(volumes['maker'])):
            if volume<volumes['maker'][cnt]:
                fees['maker']=fee_multifliers['maker'][cnt-1]
                break
        return fees

    def order_list(self,currency_pair=None, current_page=1, page_length=200):
        # symbol, page, type are optional
        # https://openapi.digifinex.vip/v2/open_orders?symbol=usdt_btc&page=1&apiKey=59328e10e296a&timestamp=1410431266&sign=0a8d39b515fd8f3f8b848a4c459884c2

        ORDER_LIST_RESOURCE='/v2/open_orders'
        params={}
        params['timestamp']=str(time.time())
        if currency_pair:
            params['symbol']= make_currency_pair_string(currency_pair)
        if current_page:
            params['page']=str(current_page)
        params['sign']=sign(self.account,params)

        result = requests.get(self.base_url + ORDER_LIST_RESOURCE, params)
        result = universal.SubmittedOrderList(currency_pair, self.MARKET, result.text )
        return result

    def trade_list(self,currency_pair, current_page=1, page_length=200):
        # TO BE IMPLEMENTED
        pass