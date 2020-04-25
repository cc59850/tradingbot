# -*- coding: UTF-8 -*-
import sys
sys.path.append("..")
import time

class Exchange:

    _market=None
    MARKET_BASEURL_MAPPING={
        'AEX':'https://api.aex.zone',
        'OKEx': 'www.okex.com',
        'DigiFinex':'https://openapi.digifinex.vip',
        'Kraken':'wss://ws.kraken.com/', # this is a web socket subscription url
        'Binance':'https://api.binance.com',
        'Kucoin':'https://api.kucoin.com',
        'Huobi':'https://api.huobi.pro',
        'Liquid':'https://api.liquid.com',
        'Okex':'https://www.okex.com',
        'Coinbase':'https://api.pro.coinbase.com',
        'Bitfinex':'https://api.bitfinex.com/v1',
        'KrakenRest':'https://api.kraken.com',
        'Bitstamp':'https://www.bitstamp.net',
        'Gateio':'https://data.gateio.co',
        'Bittrex':'https://api.bittrex.com',
        'Poloniex':'https://poloniex.com',
        'Itbit':'https://api.itbit.com',
        'Bitso':'https://api.bitso.com',
        'Zb':'http://api.zb.cn',
        'Binance':'https://api.binancezh.com',


    }

    def __init__(self, account, base_url=None):
        self.account = account
        if not base_url is None:
            self.base_url = base_url

    def get_currency_pairs_info(self):
        pass

    def ticker(self, currency_pair):
        pass

    def depth(self, currency_pair, raw=True):
        pass

    def trades(self, currency_pair):
        pass

    def balances(self):
        pass

    def submit_order(self, type, currency_pair, price, amount):
        pass

    def order_list(self,currency_pair, current_page=1, page_length=200):
        pass

    def trade_list(self,currency_pair, current_page=1, page_length=200):
        pass
