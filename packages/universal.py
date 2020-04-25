# encoding=utf-8
# this project is powered by Jeff Omega
# as author is a newbie to python, code style of this project is rubyish
# as a convention, class name is capitalized and instance is lower-cased
# and this project is migrated from btc38_1 project which is forked from
# a btc38 gem from github

import sys

sys.path.append("..")
from packages import error_code
import json
import time
import math
import copy
from packages import digifinex as DIGIFINEX
from packages import currency_pair as CP


class OrderInfo:
    def __init__(self, market, currency_pair, result, params):
        try:
            market = str(market).lower()
            if market == 'okex':
                result = json.loads(result)
                self.order_id = ""
                if result.__contains__("result") and result["result"] == True:
                    self.order_id = result["order_id"]
                    self.price = params["price"]
                    self.amount = params["amount"]
                    self.type = params["type"]
                    self.message = "操作成功"
                else:
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
                    self.message = result["error_code"]
            if market == 'aex':
                self.order_id = ""
                if len(result) > 0:
                    if str(result[0]).find('succ') != -1:
                        result = str(result[0], 'utf-8')
                        self.order_id = result.split('|')[1]
                        self.price = params["price"]
                        self.amount = params["amount"]
                        self.type = params["type"]
                        self.message = "操作成功"
                    if str(result[0]).find('overBalance') != -1:
                        self.message = "操作失败，余额不足"
                else:
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
                    self.message = result["error_code"]
            if market == 'digifinex':
                result = json.loads(result)
                self.order_id = ""
                if result['code'] == 0:
                    self.order_id = result['order_id']
                    self.price = params["price"]
                    self.amount = params["amount"]
                    self.type = params["type"]
                    self.message = "操作成功"
                else:
                    self.message = error_code.Error_code_for_DigiFinex[result["code"]]
            if market == 'kraken':
                if result.__contains__('error') and len(result['error']) > 0:
                    self.message = result['error'][0]
                else:
                    self.order_id = result['result']['txid'][0]
                    self.price = params["price"]
                    self.amount = params["amount"]
                    self.type = params["type"]
                    self.message = "操作成功"
        except Exception as e:
            self.order_ids = []
            self.message = e
            print(e)


#  this class represents the orders that you HAVE already submitted,
# NOT the orders you are submitting!!!
class SubmittedOrderList:
    def __init__(self, currency_pair, market, result):
        market = str(market).lower()
        if market == 'okex':
            result = json.loads(result)
            if result.__contains__("result") and result["result"] == True:
                if result.__contains__("total"):
                    self.orders = []
                    self.total = result["total"]
                    orders = result["orders"]
                    for order in orders:
                        currency_pair = order["symbol"]
                        id = int(order["order_id"])
                        price = float(order["price"])
                        total_amount = float(order["amount"])
                        trade_amount = float(order["deal_amount"])
                        status = int(order["status"])
                        trade_price = float(order["avg_price"])
                        trade_money = trade_amount * trade_price
                        trade_type = (1 if order["type"] == "buy" else 0)
                        this_order = SubmittedOrder(currency_pair, id, price, status, total_amount, trade_amount,
                                                    trade_money, trade_price, trade_type)
                        self.orders.append(this_order)
                        self.message = "操作成功"
            else:
                self.message = error_code.Error_code_for_OKEx[result["error_code"]]
        if market == 'aex':
            # TODO: 下面的遍历中的SubmittedOrder实例化方法传参不太对，需要对原始数据进行详尽分析才能正确生成
            if len(result) >= 0:
                self.orders = []
                self.total = len(result)
                for order in result:
                    order_ = json.loads(str(order, 'utf-8'))[0]
                    id = order_['id']
                    price = float(order_['price'])
                    amount = float(order_['amount'])
                    type = int(order_['type'])
                    this_order = SubmittedOrder(currency_pair, id, price, 0, amount, amount, 0, price, type)
                    self.orders.append(this_order)
                self.message = '操作成功'
            else:
                self.message = error_code.Error_code_for_OKEx[result["error_code"]]
        if market == 'digifinex':
            result = json.loads(result)
            if result['code'] == 0:
                self.orders = []
                for order in result['orders']:
                    currency_pair = CP.CurrencyPair(str(order['symbol']).split('_')[1],
                                                    str(order['symbol']).split('_')[0])
                    id = order['order_id']
                    price = float(order['price'])
                    total_amount = float(order['amount'])
                    trade_amount = float(order['executed_amount'])
                    status = int(order['status'])
                    trade_price = float(order['avg_price'])
                    trade_money = float(order['cash_amount'])
                    trade_type = (1 if order["type"] == "buy" else 0)
                    this_order = SubmittedOrder(currency_pair, id, price, status, total_amount, trade_amount,
                                                trade_money, trade_price, trade_type)
                    self.orders.append(this_order)
                self.message = '操作成功'
            else:
                self.message = error_code.Error_code_for_DigiFinex[result['code']]


class SubmittedOrder:
    def __init__(self, currency_pair, id, price, status, total_amount,
                 trade_amount, trade_money, trade_price, trade_type):
        self.currency_pair = currency_pair
        self.id = id
        self.price = price
        self.status = status
        self.total_amount = total_amount
        self.trade_amount = trade_amount
        self.trade_money = trade_money
        self.trade_price = trade_price
        self.trade_type = trade_type


class CancelOrderResult:
    def __init__(self, market, currency_pair, result, order_id):
        self.currency_pair = currency_pair
        market = str(market).lower()
        if market == "chbtc":
            pass
        if market == "okex":
            result = json.loads(result)
            if result.__contains__("result"):
                self.result = True
                self.message = "操作成功"
                self.id = order_id
            else:
                self.result = False
                self.message = error_code.Error_code_for_OKEx[result["error_code"]]
                self.id = order_id
        if market == "aex":
            if len(result) == 0:
                self.result = False
                self.message = "操作失败"
                self.id = order_id
            else:
                result = str(result[0], 'utf-8')
                if result.find('succ') != -1:
                    self.result = True
                    self.message = "操作成功"
                    self.id = order_id
                else:
                    self.result = False
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
                    self.id = order_id
        if market == "digifinex":
            result = json.loads(result)
            if result['code'] == 0:
                self.message = '操作成功'
                self.successful_orders_ids = result['success']
                self.failed_orders_ids = result['error']
            else:
                self.failed_orders_ids = order_id
                self.message = error_code.Error_code_for_DigiFinex[result['code']]
        if market == 'kraken':
            if len(result['error']) > 0:
                self.message = result['error'][0]
            else:
                self.message = '操作成功'
                self.id = order_id


class Order:
    def __init__(self, price, amount):
        self.price = float(price)
        self.amount = float(amount)


class Bid(Order):
    pass


class Ask(Order):
    pass


def api_update_book(api_book, side, data, depth_length=100):
    for x in data:
        price_level = x[0]
        if float(x[1]) != 0.0:
            api_book[side].update({price_level: float(x[1])})
        else:
            if price_level in api_book[side]:
                api_book[side].pop(price_level)
    if side == "bid":
        api_book["bid"] = dict(sorted(api_book["bid"].items(), reverse=True)[:int(depth_length)])
    elif side == "ask":
        api_book["ask"] = dict(sorted(api_book["ask"].items())[:int(depth_length)])
    return api_book


class Depth(object):

    @classmethod
    def fromResponses(cls, market, currency_pair, responses, flags):
        ass = []
        bss = []
        for item in responses:
            result = copy.deepcopy(item)
            result = list(json.loads(result))
            if len(result) < 2:
                continue
            if result[-2] == flags['depth'] and result[-1] == flags['currency_pair']:
                _result = result[1]
                if isinstance(result[2], dict) == True:
                    _result.update(result[2])
            _result = dict(_result)
            if _result.__contains__('as'):
                ass = _result['as']
            if _result.__contains__('bs'):
                bss = _result['bs']
            if _result.__contains__('a'):
                for a in _result['a']:
                    price = a[0]
                    amount = a[1]
                    is_a_existed_in_a1 = False
                    for a1 in ass:
                        if a1[0] == price:
                            a1[1] = amount
                            is_a_existed_in_a1 = True
                            continue
                    if is_a_existed_in_a1 == False:
                        ass.append(a)

            if _result.__contains__('b'):
                for b in _result['b']:
                    price = b[0]
                    amount = b[1]
                    is_b_existed_in_b1 = False
                    for b1 in bss:
                        if b1[0] == price:
                            b1[1] = amount
                            is_b_existed_in_b1 = True
                            continue
                    if is_b_existed_in_b1 == False:
                        bss.append(b)
            break_point = None
        ass = list(filter(lambda x: float(x[1]) != 0, ass))
        bss = list(filter(lambda x: float(x[1]) != 0, bss))
        ass = sorted(ass, key=lambda x: x[0], reverse=False)
        bss = sorted(bss, key=lambda x: x[0], reverse=True)
        asks = []
        bids = []
        for a in ass:
            ask = Ask(a[0], a[1])
            asks.append(ask)
        for b in bss:
            bid = Bid(b[0], b[1])
            bids.append(bid)
        return Depth(market, currency_pair, None, bids, asks)
        break_point = None

    @classmethod
    def filter(cls, depths):
        '''
        by analyzing several depths, this method determines a Depth instance that is most likely to be an accurate one
        which filters out the flash orders
        :param depths: a list of depths which is ordered by time
        :return: A Depth instance
        '''
        num_depths = len(depths)
        asks = []
        bids = []

        # record every price
        for bid in depths[0].bids:
            price = bid.price
            amount = bid.amount
            weight = 1  # after having iterated all bids of other depths and find a bid that has the same price as this one, flag+=1
            for cnt in range(1, len(depths)):
                for bid1 in depths[cnt].bids:
                    if bid1.price == price:
                        amount = min(amount, bid1.amount)
                        weight += 1
            if weight == len(depths):
                bids.append(Bid(price, amount))

        for ask in depths[0].asks:
            price = ask.price
            amount = ask.amount
            weight = 1  # after having iterated all bids of other depths and find a bid that has the same price as this one, flag+=1
            for cnt in range(1, len(depths)):
                for ask1 in depths[cnt].asks:
                    if ask1.price == price:
                        amount = min(amount, ask1.amount)
                        weight += 1
            if weight == len(depths):
                asks.append(Ask(price, amount))

        result_depth = Depth(
            market=depths[0].market,
            currency_pair=depths[0].currency_pair,
            result=None,
            asks=asks,
            bids=bids
        )
        return result_depth
        pass

    @classmethod
    def get_supporting_points(cls, depth, weighted_by='vol', distance=1):
        if weighted_by == 'vol':
            acc_bid_vol = 0
            acc_ask_vol = 0
            cnt = 0
            bid_price = depth.bids[
                -1].price  # in case can not find a proper point, set this price to a very distant price in the 1st place
            ask_price = depth.asks[-1].price
            for bid in depth.bids:
                acc_bid_vol += bid.amount
                if acc_bid_vol >= distance:
                    bid_price = bid.price
                    break
            for ask in depth.asks:
                acc_ask_vol += ask.amount
                if acc_ask_vol >= distance:
                    ask_price = ask.price
                    break
            supporting_points = [bid_price, ask_price]
            return supporting_points
        if weighted_by == 'price':
            mid_price = (depth.asks[0].price + depth.bids[0].price) / 2
            price_gap = 99999
            ask_price = None
            bid_price = None
            bid_vol_from_0 = 0
            ask_vol_from_0 = 0
            ask_accumulative_vol = 0
            bid_accumulative_vol = 0
            diff_ask_vol_and_bid_vol = 99999
            diff_bid_vol_and_ask_vol = 99999
            supporting_points_from_ask = []
            supporting_points_from_bid = []

            for ask in depth.asks:
                ask_price = ask.price
                ask_accumulative_vol += ask.amount
                target_bid_price = ask_price - distance * 2
                delta_bid_price = 99999
                bid_accumulative_vol = 0
                _diff_ask_vol_and_bid_vol = 99999
                for bid in depth.bids:
                    _delta_bid_price = abs(bid.price - target_bid_price)
                    if _delta_bid_price > delta_bid_price:
                        _diff_ask_vol_and_bid_vol = abs(ask_accumulative_vol - bid_accumulative_vol)
                        break
                    else:
                        bid_price = bid.price
                        bid_accumulative_vol += bid.amount
                        delta_bid_price = _delta_bid_price
                if _diff_ask_vol_and_bid_vol > diff_ask_vol_and_bid_vol:
                    supporting_points_from_ask = [bid_price, ask_price]
                else:
                    diff_ask_vol_and_bid_vol = _diff_ask_vol_and_bid_vol

            for bid in depth.bids:
                bid_price = bid.price
                bid_accumulative_vol += bid.amount
                target_ask_price = bid_price + distance * 2
                delta_ask_price = 99999
                ask_accumulative_vol = 0
                _diff_bid_vol_and_ask_vol = 99999
                for ask in depth.asks:
                    _delta_ask_price = abs(ask.price - target_ask_price)
                    if _delta_ask_price > delta_ask_price:
                        _diff_bid_vol_and_ask_vol = abs(bid_accumulative_vol - ask_accumulative_vol)
                        break
                    else:
                        ask_price = ask.price
                        ask_accumulative_vol += ask.amount
                        delta_ask_price = _delta_ask_price
                if _diff_bid_vol_and_ask_vol > diff_bid_vol_and_ask_vol:
                    supporting_points_from_bid = [bid_price, ask_price]
                else:
                    diff_bid_vol_and_ask_vol = _diff_bid_vol_and_ask_vol

            if diff_bid_vol_and_ask_vol > diff_ask_vol_and_bid_vol:
                return supporting_points_from_ask
            else:
                return supporting_points_from_bid
            # if price_gap>distance*2:
            #     for ask in depth.asks:
            #         if ask.price<=distance+mid_price:
            #             ask_vol_from_0+=ask.amount
            #             ask_price=ask.price
            #     for bid in depth.bids:
            #         if bid.price>=mid_price-distance:
            #             bid_vol_from_0+=bid.amount
            #             bid_price=bid.price
            #     diff_vol_from_0=ask_vol_from_0-bid_vol_from_0
            #     bid_vol_from_0=bid_vol_from_0-diff_vol_from_0/2
            #     ask_vol_from_0=ask_vol_from_0+diff_vol_from_0/2
            #
            #     price_gap=ask_price-bid_price
            #

    def __init__(self, market, currency_pair, result=None, bids=[], asks=[]):
        '''
        the Depth class instance has the following data members:
        bids:  Array of Bid
        asks:  Array of Ask
        timestamp:  Long
        message:  String
        market:  String
        currency_pair:  String
        :param market:  represents which market you are in
        :param currency_pair: represents which currency pair you are trading with
        :param result: represents the json that the server returns to you
        '''
        if result is None:
            self.bids = bids
            self.asks = asks
            self.timestamp = int(time.time())
            self.market = market
            self.currency_pair = currency_pair
            self.message = "True"
            return
        self.bids = []
        self.asks = []
        self.timestamp = int(time.time())
        self.market = market
        self.currency_pair = currency_pair
        self.message = "True"
        try:
            market = str(market).lower()
            # result=json.loads(str(result))
            if market == "liquid":
                result = json.loads(result)
                if dict(result).__contains__('buy_price_levels'):
                    bss = result['buy_price_levels']  # the bids object in the json
                    ass = result['sell_price_levels']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b[0], b[1])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a[0], a[1])
                        self.asks.append(ask)
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            if market == "zb":
                result = json.loads(result)
                if dict(result).__contains__('asks'):
                    bss = result['bids']  # the bids object in the json
                    ass = result['asks']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b[0], b[1])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a[0], a[1])
                        self.asks.append(ask)
                    self.asks.reverse()
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            if market == "bitso":
                result = json.loads(result)
                if dict(result)['success'] == True:
                    result = result['payload']
                    bss = result['bids']  # the bids object in the json
                    ass = result['asks']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b['price'], b['amount'])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a['price'], a['amount'])
                        self.asks.append(ask)
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            if market == "itbit":
                result = json.loads(result)
                if dict(result).__contains__('asks'):
                    bss = result['bids']  # the bids object in the json
                    ass = result['asks']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b[0], b[1])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a[0], a[1])
                        self.asks.append(ask)
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            if market == "poloniex":
                result = json.loads(result)
                if dict(result).__contains__('asks'):
                    bss = result['bids']  # the bids object in the json
                    ass = result['asks']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b[0], b[1])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a[0], a[1])
                        self.asks.append(ask)
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            if market == "bittrex":
                result = json.loads(result)
                if dict(result)['success'] == True:
                    bss = result['result']['buy']  # the bids object in the json
                    ass = result['result']['sell']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b['Rate'], b['Quantity'])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a['Rate'], a['Quantity'])
                        self.asks.append(ask)
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            if market == "gateio":
                result = json.loads(result)
                if dict(result).__contains__("asks"):
                    bss = result['bids']  # the bids object in the json
                    ass = result['asks']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b[0], b[1])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a[0], a[1])
                        self.asks.append(ask)
                    self.asks.reverse()
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            if market == "bitstamp":
                result = json.loads(result)
                if dict(result).__contains__("asks"):
                    bss = result['bids']  # the bids object in the json
                    ass = result['asks']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b[0], b[1])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a[0], a[1])
                        self.asks.append(ask)
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            if market == "bitfinex":
                result = json.loads(result)
                if dict(result).__contains__("asks"):
                    bss = result['bids']  # the bids object in the json
                    ass = result['asks']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b['price'], b['amount'])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a['price'], a['amount'])
                        self.asks.append(ask)
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            if market == "coinbase":
                result = json.loads(result)
                if dict(result).__contains__("asks"):
                    bss = result['bids']  # the bids object in the json
                    ass = result['asks']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b[0], b[1])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a[0], a[1])
                        self.asks.append(ask)
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            if market == "okex":
                result = json.loads(result)
                if dict(result).__contains__("asks"):
                    bss = result['bids']  # the bids object in the json
                    ass = result['asks']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b[0], b[1])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a[0], a[1])
                        self.asks.append(ask)
                    self.asks.reverse()
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            if market == "binance":
                result = json.loads(result)
                if result.__contains__("asks"):
                    bss = result['bids']  # the bids object in the json
                    ass = result['asks']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b[0], b[1])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a[0], a[1])
                        self.asks.append(ask)
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            if market == "kucoin":
                result = json.loads(result)
                if result['code'] == '200000':
                    result = result['data']
                    bss = result['bids']  # the bids object in the json
                    ass = result['asks']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b[0], b[1])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a[0], a[1])
                        self.asks.append(ask)
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            if market == "huobi":
                result = json.loads(result)
                if result['status'] == 'ok':
                    result = result['tick']
                    bss = result['bids']  # the bids object in the json
                    ass = result['asks']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b[0], b[1])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a[0], a[1])
                        self.asks.append(ask)
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            elif market == "kraken":
                self.asks = []
                self.bids = []
                for a in result['ask'].keys():
                    ask = Ask(a, result['ask'][a])
                    self.asks.append(ask)
                for b in result['bid'].keys():
                    bid = Bid(b, result['bid'][b])
                    self.bids.append(bid)
                self.bids.sort(key=lambda x: x.price, reverse=True)
                self.asks.sort(key=lambda x: x.price, reverse=False)
            elif market == "krakenrest":
                result = json.loads(result)
                if len(result['error']) != 0:
                    self.message = result['error'][0]
                    return
                from packages import kraken_rest1 as KR
                symbol = list(dict(result['result']).keys())[0]
                result = result['result'][symbol]
                self.asks = []
                self.bids = []
                for a in result['asks']:
                    ask = Ask(a[0], a[1])
                    self.asks.append(ask)
                for b in result['bids']:
                    bid = Bid(b[0], b[1])
                    self.bids.append(bid)
                self.bids.sort(key=lambda x: x.price, reverse=True)
                self.asks.sort(key=lambda x: x.price, reverse=False)
            elif market == "aex":
                result = json.loads(str(result))
                if result.__contains__("asks"):
                    bss = result['bids']  # the bids object in the json
                    ass = result['asks']  # the asks object in the json
                    for b in bss:
                        bid = Bid(b[0], b[1])
                        self.bids.append(bid)
                    for a in ass:
                        ask = Ask(a[0], a[1])
                        self.asks.append(ask)
                elif dict(result).__contains__("error_code"):
                    self.message = error_code.Error_code_for_OKEx[result["error_code"]]
            elif market == "digifinex":
                result = json.loads(str(result))
                # self.timestamp = result['date']
                self.message = "操作成功"

                bss = result['bids']  # the bids object in the json
                ass = result['asks']  # the asks object in the json
                for b in bss:
                    bid = Bid(b[0], b[1])
                    self.bids.append(bid)
                for a in ass:
                    ask = Ask(a[0], a[1])
                    self.asks.append(ask)
                self.asks.reverse()
        except Exception as e:
            self.message = e
            print(e)
        finally:
            pass

    def __sub__(self, other):
        import copy
        result = copy.deepcopy(self)
        size_of_bids = len(result.bids)
        size_of_asks = len(result.asks)
        if other.__class__ is Depth:
            for bid in other.bids:
                price = bid.price
                amount = bid.amount
                cnt = 0
                while cnt < size_of_bids:
                    if result.bids[cnt].price == price:
                        result.bids[cnt].amount -= amount
                    cnt += 1

            for ask in other.asks:
                price = ask.price
                amount = ask.amount
                cnt = 0
                while cnt < size_of_asks:
                    if result.asks[cnt].price == price:
                        result.asks[cnt].amount -= amount
                    cnt += 1
        else:
            pass

    def __add__(self, other):
        '''
        untested!!!!!
        :param other:
        :return:
        '''
        import copy
        this = copy.deepcopy(self)
        if other.currency_pair.toString() != this.currency_pair.toString():
            raise Exception('Depths of different currency pairs can not be added')
        this.bids.extend(other.bids)
        this.asks.extend(other.asks)
        this.bids.sort(key=lambda x: x.price, reverse=True)
        this.asks.sort(key=lambda x: x.price, reverse=True)
        return this

    def update(self, other):
        '''
        PASSED
        update self.bids and self.asks with items in other.bids or asks
        :param other:
        :return:
        '''
        if other.currency_pair.toString() != self.currency_pair.toString():
            raise Exception('Depths of different currency pairs can not be added')
        this = copy.deepcopy(self)
        for ask in other.asks:
            price = ask.price
            amount = ask.amount
            flag = False
            for ask1 in this.asks:
                if abs(ask1.price - price) < 0.00001:
                    ask1.amount = amount
                    flag = True

            if flag == False:
                this.asks.append(ask)
        this.asks = list(filter(lambda x: x.amount != 0, this.asks))
        this.asks.sort(key=lambda x: x.price, reverse=False)

        for bid in other.bids:
            price = bid.price
            amount = bid.amount
            flag = False
            for bid1 in this.bids:
                if abs(bid1.price - price) < 0.00001:
                    bid1.amount = amount
                    flag = True
            if flag == False:
                this.bids.append(bid)
        this.bids = list(filter(lambda x: x.amount != 0, this.bids))
        this.bids.sort(key=lambda x: x.price, reverse=True)
        return this

    def is_consumed_by(self, trades):
        length = len(trades.trades)
        for trade in trades.trades:
            price = trade.price
            amount = trade.amount
            trade_type = trade.trade_type
            if trade_type == 1:
                for ask in self.asks:
                    if abs(ask.price - price) < 0.0001:
                        ask.amount -= amount
            else:
                for bid in self.bids:
                    if abs(bid.price - price) < 0.0001:
                        bid.amount -= amount
        # trades.trades=trades.trades[length:]
        return self
        # def get_supporting_points(self, weighted_by=None, distance=1, referencial_currency=''):

    #     CONSTANT=1
    #     if referencial_currency=='usdt':
    #         CONSTANT=10000
    #     supporting_points=[0,0]
    #     if weighted_by==None:
    #         ask0=self.asks[0].price
    #         bid0=self.bids[0].price
    #         my_ask=99999
    #         my_bid=0
    #
    #         if ask0-bid0<=0.00000002*CONSTANT:
    #             my_ask=ask0
    #             my_bid=bid0
    #         else:
    #             my_ask=ask0-0.00000001*CONSTANT
    #             my_bid=bid0+0.00000001*CONSTANT
    #         return [my_bid,my_ask]
    #     elif weighted_by=="vol":
    #         acc_bid_vol=0
    #         acc_ask_vol=0
    #         cnt=0
    #         bid_price=self.bids[-1].price  # in case can not find a proper point, set this price to a very distant price in the 1st place
    #         ask_price=self.asks[-1].price
    #         for bid in self.bids:
    #             acc_bid_vol+=bid.amount
    #             if acc_bid_vol>=distance:
    #                 bid_price=bid.price
    #                 break
    #         for ask in self.asks:
    #             acc_ask_vol+=ask.amount
    #             if acc_ask_vol>=distance:
    #                 ask_price=ask.price
    #                 break
    #         supporting_points=[bid_price,ask_price]
    #         return supporting_points
    '''
    here distance means accumulated amount, e.g:
    bid0: 0.1
    bid1: 0.05
    bid2: 0.11
    bid3: 0.07
    here, if the distance is 0.2, 
    bid0+bid1+bid2 is just beyond the distance, then
    the price of bid3 is the target price
    
    but when you think about it, you dont really need this function,
    because before long, you would use tensorflow as the backend to
    calculate and deduce the pattern, then this strategy is useless!
    
    but anyway, you have to use this function before you implement this into tensorflow...............
    '''


class Kline:
    def __init__(self, o, c, h, l, v, timestamp):
        self.open = o
        self.close = c
        self.high = h
        self.low = l
        self.vol = v
        self.timestamp = timestamp


class KlineWithVol(Kline):
    def __init__(self, o, c, h, l, v, timestamp, vol_bid, vol_ask, avg_buy=None, avg_sell=None, avg_amount_per_trade=None):
        self.open = o
        self.close = c
        self.high = h
        self.low = l
        self.vol = v
        self.timestamp = timestamp
        self.vol_bid = vol_bid
        self.vol_ask = vol_ask
        self.avg_buy=avg_buy
        self.avg_sell=avg_sell
        self.avg_amount_per_trade=avg_amount_per_trade

class Klines:
    '''
    作者：纽润量化团队
    问题分析：
        0. k线的构成要素： OHLC+Volume+顶部成交量+底部成交量+可触及的高点、低点
        1. 按照什么生成k线序列？
            1.1 按照等时间间隔，例如1分钟生成一根k线
            1.2 按照成交量，例如每100btc成交量生成一根k线，或者每100000美元生成一根k线
            1.3 按照笔数（存疑），例如每1000笔交易生成一根k线
            1.4 按照波动区间生成k线
        2.
    '''

    def __init__(self, market, currency_pair, result):
        self.market = market
        self.currency_pair = currency_pair
        self.message = 'Unknow error'
        self.klines = []
        try:
            for item in result:
                kline = Kline(timestamp=item[0], o=item[1], h=item[2], l=item[3], c=item[4], v=item[5])
                self.klines.append(kline)
            self.message = '操作成功'
        except:
            error_key = result["error_code"]
            self.message = error_code.Error_code_for_OKEx[error_key]

    @classmethod
    def from_db(cls, tablename):
        pass

    @classmethod
    def from_trades(cls, currency_pair, trades, aggregated_by='price', distance=20, accumulative_vol=0.01):
        _trades = []
        if trades.__class__ == list:
            for row in trades:
                trade = TradeInfo(row[3], row[5], row[6], row[4], row[2], row[7])
                _trades.append(trade)
            trades = _trades
            market = row[1]
            klines = Klines(market, currency_pair, [])
        else:
            klines = Klines('None', currency_pair, [])
        if aggregated_by == 'price':
            currenct_price = trades.trades[0].price
            current_timestamp = trades.trades[0].timestamp
            bid_vol_at_peak = 0
            ask_vol_at_bottom = 0
            peak = -9999999
            bottom = 9999999
            open = None
            close = None
            high = None
            low = None
            vol = 0
            for cnt in range(0, len(trades.trades)):
                trade = trades.trades[cnt]
                trade_type = trade.trade_type
                amount = trade.amount
                price = trade.price
                vol += amount
                if open is None:
                    open = price
                if close is None:
                    close = price
                if high is None:
                    high = price
                if low is None:
                    low = price
                if trade_type == 1:
                    if price > high:
                        high = price
                        bid_vol_at_peak = amount
                    elif price == high:
                        bid_vol_at_peak += amount
                    else:
                        pass
                else:
                    if price < low:
                        low = price
                        ask_vol_at_bottom = amount
                    elif price == low:
                        ask_vol_at_bottom += amount
                    else:
                        pass
                timestamp = trade.timestamp
                if distance < 1:
                    absolute_distance = distance * price
                else:
                    absolute_distance = distance
                if high - low >= absolute_distance:  # and bid_vol_at_peak>=accumulative_vol and ask_vol_at_bottom>=accumulative_vol:
                    close = price
                    kline = Kline(open, close, high, low, vol, timestamp)
                    klines.klines.append(kline)
                    vol = 0
                    bid_vol_at_peak = 0
                    ask_vol_at_bottom = 0
                    open = None
                    close = None
                    high = None
                    low = None
            return klines
        if aggregated_by == "volume":
            vol_buy = 0
            vol_sell = 0
            money_buy = 0
            money_sell = 0
            trades_count = 0
            open = None
            close = None
            high = None
            low = None
            vol = 0
            for cnt in range(0, len(trades)):
                trade = trades[cnt]
                trade_type = trade.trade_type
                amount = trade.amount
                price = trade.price
                vol += amount
                if open is None:
                    open = price
                if close is None:
                    close = price
                if high is None:
                    high = price
                if low is None:
                    low = price
                if price > high:
                    high = price
                if price < low:
                    low = price
                trades_count+=1
                if trade_type == 1:
                    vol_buy+=amount
                    money_buy+=amount*price
                else:
                    vol_sell+=amount
                    money_sell+=amount*price
                timestamp = trade.timestamp
                if distance < 1:
                    absolute_distance = distance * price
                else:
                    absolute_distance = distance
                if vol >= distance :  # and bid_vol_at_peak>=accumulative_vol and ask_vol_at_bottom>=accumulative_vol:
                    close = price
                    avg_buy = money_buy / vol_buy if vol_buy != 0 else low
                    avg_sell = money_sell / vol_sell if vol_sell != 0 else high
                    avg_amount = vol / trades_count
                    kline = KlineWithVol(open, close, high, low, vol, timestamp, vol_buy, vol_sell, avg_buy, avg_sell, avg_amount)
                    klines.klines.append(kline)
                    vol_buy = 0
                    vol_sell = 0
                    money_buy = 0
                    money_sell = 0
                    trades_count = 0
                    vol = 0
                    open = None
                    close = None
                    high = None
                    low = None
            return klines
        if aggregated_by == "equal_price":
            currenct_price = trades[0].price
            current_timestamp = trades[0].timestamp
            bid_vol_at_peak = 0
            ask_vol_at_bottom = 0
            vol_buy=0
            vol_sell=0
            money_buy=0
            money_sell=0
            trades_count=0
            peak = -9999999
            bottom = 9999999
            open = None
            close = None
            high = None
            low = None
            vol = 0
            for cnt in range(0, len(trades)):
                trade = trades[cnt]
                trade_type = trade.trade_type
                amount = trade.amount
                price = trade.price
                vol += amount
                trades_count+=1
                if open is None:
                    open = price
                if close is None:
                    close = price
                if high is None:
                    high = price
                if low is None:
                    low = price
                if price > high:
                    high = price
                if price < low:
                    low = price
                if trade_type == 1:
                    vol_buy+=amount
                    money_buy+=amount*price
                else:
                    vol_sell+=amount
                    money_sell+=amount*price

                timestamp = trade.timestamp
                if distance < 1:
                    absolute_distance = distance * price
                else:
                    absolute_distance = distance
                if abs(open - price) >= distance and vol>30:  # and bid_vol_at_peak>=accumulative_vol and ask_vol_at_bottom>=accumulative_vol:
                    close = price
                    avg_buy = money_buy / vol_buy if vol_buy != 0 else low
                    avg_sell = money_sell / vol_sell if vol_sell != 0 else high
                    avg_amount=vol/trades_count
                    kline=KlineWithVol(open,close,high,low,vol,timestamp,vol_buy,vol_sell,avg_buy,avg_sell,avg_amount)
                    klines.klines.append(kline)
                    vol = 0
                    vol_sell = 0
                    vol_buy=0
                    money_sell=0
                    money_buy=0
                    trades_count=0
                    open = None
                    close = None
                    high = None
                    low = None
            return klines
        if aggregated_by == "time":
            currenct_price = trades[0].price
            previous_timestamp = trades[0].timestamp
            vol_buy = 0
            vol_sell = 0
            money_buy = 0
            money_sell = 0
            trades_count = 0
            open = None
            close = None
            high = None
            low = None
            vol = 0

            for cnt in range(0, len(trades)):
                trade = trades[cnt]
                trade_type = trade.trade_type
                amount = trade.amount
                price = trade.price
                vol += amount
                trades_count+=1
                if open is None:
                    open = price
                if close is None:
                    close = price
                if high is None:
                    high = price
                if low is None:
                    low = price
                if trade_type == 1:
                    vol_buy += amount
                    money_buy+=amount*price
                    if price > high:
                        high = price
                        bid_vol_at_peak = amount
                    # elif price == high:
                    #     bid_vol_at_peak += amount
                    else:
                        pass
                else:
                    vol_sell += amount
                    money_sell+=amount *price
                    if price < low:
                        low = price
                        ask_vol_at_bottom = amount
                    # elif price == low:
                    #     ask_vol_at_bottom += amount
                    else:
                        pass
                timestamp = trade.timestamp
                if distance < 1:
                    absolute_distance = distance * price
                else:
                    absolute_distance = distance
                if timestamp >= previous_timestamp + distance:  # and bid_vol_at_peak>=accumulative_vol and ask_vol_at_bottom>=accumulative_vol:
                    close = price
                    avg_buy = money_buy / vol_buy if vol_buy != 0 else low
                    avg_sell = money_sell / vol_sell if vol_sell != 0 else high
                    avg_amount = vol / trades_count
                    kline = KlineWithVol(open, close, high, low, vol, timestamp, vol_buy, vol_sell, avg_buy, avg_sell,
                                         avg_amount)
                    klines.klines.append(kline)
                    vol = 0
                    vol_sell = 0
                    vol_buy = 0
                    money_sell = 0
                    money_buy = 0
                    trades_count = 0
                    open = None
                    close = None
                    high = None
                    low = None
                    previous_timestamp = previous_timestamp + distance
            return klines
        if aggregated_by == "zigzag":
            '''
            根据转折点划分k线，计算一个时间窗内的最高点最为一根k线的开盘或收盘价，
            或者一个时间窗内的最低点最为开盘或收盘价
            根据kraken的手续费3.2‰计算，每个k线的high-low至少为23美元才能勉强保本
            '''
            currenct_price = trades[0].price
            previous_timestamp = trades[0].timestamp
            bid_vol = 0
            ask_vol = 0
            open = None
            close = None
            high = None
            low = None
            vol = 0
            cnt = 0
            last_seen = 'None'
            first_cnt=0
            last_cnt=0
            while cnt < len(trades):
                trade = trades[cnt]
                trade_type = trade.trade_type
                amount = trade.amount
                price = trade.price
                vol += amount
                cnt += 1
                if open is None:
                    open = price
                if close is None:
                    close = price
                if high is None:
                    high = price
                if low is None:
                    low = price
                if trade_type == 1:
                    bid_vol += amount
                    if price > high:
                        high = price
                        last_seen = "high"
                        last_cnt = cnt
                else:
                    ask_vol += amount
                    if price < low:
                        low = price
                        last_seen = "low"
                        last_cnt = cnt
                timestamp = trade.timestamp
                if high - low >= distance and timestamp>=previous_timestamp+1:  # and bid_vol_at_peak>=accumulative_vol and ask_vol_at_bottom>=accumulative_vol:
                    if last_seen == "high" and price <= high - distance:
                        '''
                        上次到达了新高，而且此次价格已经偏离高点distance
                        '''
                        target_trades=trades[first_cnt:last_cnt]
                        close = trades[last_cnt].price
                        kline= Trades.to_kline(target_trades)
                        klines.klines.append(kline)
                        vol = 0
                        bid_vol = 0
                        ask_vol = 0
                        open = None
                        close = None
                        high = None
                        low = None
                        first_cnt = last_cnt
                        last_seen='None'
                    if last_seen == 'low' and price >= low + distance:
                        target_trades = trades[first_cnt:last_cnt]
                        close = trades[last_cnt].price
                        kline = Trades.to_kline(target_trades)
                        klines.klines.append(kline)
                        vol = 0
                        bid_vol = 0
                        ask_vol = 0
                        open = None
                        close = None
                        high = None
                        low = None
                        first_cnt = last_cnt
                        last_seen = 'None'
                    previous_timestamp = previous_timestamp + distance
            return klines
        if aggregated_by == "trades_count":
            currenct_price = trades[0].price
            current_timestamp = trades[0].timestamp
            bid_vol_at_peak = 0
            ask_vol_at_bottom = 0
            vol_buy=0
            vol_sell=0
            money_buy=0
            money_sell=0
            trades_count=0
            peak = -9999999
            bottom = 9999999
            open = None
            close = None
            high = None
            low = None
            vol = 0
            for cnt in range(0, len(trades)):
                trade = trades[cnt]
                trade_type = trade.trade_type
                amount = trade.amount
                price = trade.price
                vol += amount
                trades_count+=1
                if open is None:
                    open = price
                if close is None:
                    close = price
                if high is None:
                    high = price
                if low is None:
                    low = price
                if price > high:
                    high = price
                if price < low:
                    low = price
                if trade_type == 1:
                    vol_buy+=amount
                    money_buy+=amount*price
                else:
                    vol_sell+=amount
                    money_sell+=amount*price

                timestamp = trade.timestamp
                if distance < 1:
                    absolute_distance = distance * price
                else:
                    absolute_distance = distance
                if trades_count >= distance:  # and bid_vol_at_peak>=accumulative_vol and ask_vol_at_bottom>=accumulative_vol:
                    close = price
                    avg_buy = money_buy / vol_buy if vol_buy != 0 else low
                    avg_sell = money_sell / vol_sell if vol_sell != 0 else high
                    avg_amount=vol/trades_count
                    kline=KlineWithVol(open,close,high,low,vol,timestamp,vol_buy,vol_sell,avg_buy,avg_sell,avg_amount)
                    klines.klines.append(kline)
                    vol = 0
                    vol_sell = 0
                    vol_buy=0
                    money_sell=0
                    money_buy=0
                    trades_count=0
                    open = None
                    close = None
                    high = None
                    low = None
            return klines

class Ticker(object):
    # :market, :currency, :timestamp, :high,
    # :low, :last, :vol, :buy, :sell, :message

    def __init__(self, market, currency_pair, result):
        if str(market).lower() == 'okex':
            try:
                self.market = market
                self.currency_pair = currency_pair
                if dict(result).__contains__("ticker"):
                    ticker = result["ticker"]
                    self.buy = float(ticker["buy"])
                    self.sell = float(ticker["sell"])
                    self.vol = float(ticker["vol"])
                    self.high = float(ticker["high"])
                    self.low = float(ticker["low"])
                    self.last = float(ticker["last"])
                    self.timestamp = int(result["date"])
                    self.message = "操作成功"
                elif dict(result).__contains__("error_code"):
                    self.buy = 0
                    self.sell = 0
                    self.vol = 0
                    self.high = 0
                    self.low = 0
                    self.last = 0
                    self.timestamp = 0
                    error_key = result["error_code"]
                    self.message = error_code.Error_code_for_OKEx[error_key]
            except Exception as e:
                self.message = e
        if str(market).lower() == 'digifinex':
            try:
                self.market = market
                self.currency_pair = currency_pair
                self.timestamp = result['date']
                ticker = result['ticker'][DIGIFINEX.make_currency_pair_string(currency_pair)]
                self.buy = float(ticker["buy"])
                self.sell = float(ticker["sell"])
                self.vol = float(ticker["vol"])
                self.high = float(ticker["high"])
                self.low = float(ticker["low"])
                self.last = float(ticker["last"])
                self.message = "操作成功"

            except Exception as e:
                self.message = e
        if str(market).lower() == 'aex':
            try:
                self.market = market
                self.currency_pair = currency_pair
                result = json.loads(result)
                if result.__contains__("ticker"):
                    ticker = result["ticker"]
                    self.buy = float(ticker["buy"])
                    self.sell = float(ticker["sell"])
                    self.vol = float(ticker["vol"])
                    self.high = float(ticker["high"])
                    self.low = float(ticker["low"])
                    self.last = float(ticker["last"])
                    self.timestamp = int(time.time())
                    self.message = "操作成功"
                elif dict(result).__contains__("error_code"):
                    self.buy = 0
                    self.sell = 0
                    self.vol = 0
                    self.high = 0
                    self.low = 0
                    self.last = 0
                    self.timestamp = 0
                    error_key = result["error_code"]
                    self.message = error_code.Error_code_for_OKEx[error_key]
            except Exception as e:
                self.message = e


class TradeInfo:
    '''
    :timestamp, :price, :amount, :trade_type, :tid
    '''

    def __init__(self, timestamp, price, amount, trade_type, tid=None, status=-999):
        '''

        :param timestamp:
        :param price:
        :param amount:
        :param trade_type:
        :param tid:
        :param status: -1 for drawn, 0 for pending, 1 for partially traded, 2 for complete, 3 for 撤单处理中
        -999 for unknown
        '''
        self.timestamp = timestamp
        self.amount = float(amount)
        self.price = float(price)
        self.trade_type = int(trade_type)
        self.tid = tid
        self.status = status

    def equals(self, other):
        if self.amount == other.amount and self.price == other.price and self.timestamp == other.timestamp and self.trade_type == other.trade_type and self.tid == other.tid and self.status == other.status:
            return True
        else:
            return False


class Trades:
    '''
    this class represents a series of trades, whose attribute trades is an array of TradeInfo instances
    this class has 3 data members: :market, :currency, :trades, message
    '''
    @classmethod
    def to_kline(cls, trades):
        open=trades[0].price
        close=trades[-1].price
        timestamp=trades[0].timestamp
        high=-9999999
        low=9999999
        money_buy=0
        money_sell=0
        vol_buy=0
        vol_sell=0
        vol=0
        for trade in trades:
            vol+=trade.amount
            if trade.price>high:
                high=trade.price
            if trade.price<low:
                low=trade.price
            if trade.trade_type==1:
                vol_buy+=trade.amount
                money_buy+=trade.amount*trade.price
            else:
                vol_sell+=trade.amount
                money_sell+=trade.amount*trade.price
        avg_buy=money_buy/vol_buy if vol_buy!=0 else high
        avg_sell=money_sell/vol_sell if vol_sell!=0 else low
        avg_amount_per_trade=vol/len(trades)
        return KlineWithVol(open,close,high,low,vol,timestamp,vol_buy,vol_sell,avg_buy,avg_sell,avg_amount_per_trade)

    @classmethod
    def sectionize(cls, trades, granularity=1):
        import math
        result = {'buy': {}, 'sell': {}}
        min_price = 9999999
        max_price = 0
        for trade in trades.trades:
            min_price = min(trade.price, min_price)
            max_price = max(trade.price, max_price)
        min_price = int(min_price / granularity) * granularity
        max_price = math.ceil(max_price / granularity) * granularity
        for cnt in range(min_price, max_price + 1, granularity):
            result['buy'][cnt] = 0
            result['sell'][cnt] = 0

        for trade in trades.trades:
            trade_type = trade.trade_type
            price = trade.price
            amount = trade.amount
            index = int(price / granularity) * granularity
            if trade_type == 1:
                result['buy'][index] += amount
            else:
                result['sell'][index] += amount
        return result

    @classmethod
    def statistics(cls, trades, sectionize_by=''):

        sum_price = 0
        total_amount = 0
        num_of_transactions = 0
        num_of_buying_transactions = 0
        num_of_selling_transactions = 0
        accumulated_buying_amount = 0
        accumulated_selling_amount = 0
        accumulated_price = 0
        accumulated_buying_price = 0
        accumulated_selling_price = 0
        timespan = trades.trades[0].timestamp - trades.trades[-1].timestamp

        # define the advanced statistical data
        # assume that the number of samples in each group should be 600
        seperations = [0]
        _trades = copy.deepcopy(trades.trades)
        _trades.sort(key=lambda x: x.amount, reverse=False)
        # sectionize by num of transactions, the num is set to NUM_OF_SAMPLES
        if sectionize_by == 'volume':
            seperations = [0]
            for cnt in range(0, 300, 1):
                index = cnt / 100
                seperations.append(index)
            seperations.append(10 ** 5)
        elif sectionize_by == 'both':
            seperations = [0]
            current_amount = 0.1
            num_of_samples = 0
            for cnt in range(1, int(len(_trades))):
                num_of_samples += 1
                if num_of_samples >= 600 and _trades[cnt].amount >= current_amount:
                    seperations.append(current_amount)
                    current_amount += 0.1
                    num_of_samples = 0
            seperations.append(10 ** 5)
        else:
            NUM_OF_SAMPLES = 600
            for cnt in range(0, int(len(_trades) / NUM_OF_SAMPLES)):
                index = NUM_OF_SAMPLES - 1 + cnt * NUM_OF_SAMPLES
                if index >= len(_trades):
                    index = -1
                seperations.append(_trades[index].amount)
        # sectionize by volume, the volume increases by 0.01 every step

        avg_buy_by_section_amount = {}
        avg_sell_by_section_amount = {}
        total_buy_amount_by_section_amount = {}
        total_sell_amount_by_section_amount = {}
        total_buy_by_amount_by_section_amount = {}
        total_sell_by_amount_by_section_amount = {}
        # end definition

        for cnt in range(1, len(seperations)):
            avg_buy_by_section_amount[str(seperations[cnt])] = None
            avg_sell_by_section_amount[str(seperations[cnt])] = None
            total_buy_amount_by_section_amount[str(seperations[cnt])] = 0
            total_sell_amount_by_section_amount[str(seperations[cnt])] = 0
            total_buy_by_amount_by_section_amount[str(seperations[cnt])] = 0
            total_sell_by_amount_by_section_amount[str(seperations[cnt])] = 0
        for trade in trades.trades:
            num_of_transactions += 1
            sum_price += trade.price
            total_amount += trade.amount
            accumulated_price += trade.price * trade.amount
            if trade.trade_type == 1:
                num_of_buying_transactions += 1
                accumulated_buying_amount += trade.amount
                accumulated_buying_price += trade.price * trade.amount
                amount = trade.amount
                for cnt in range(1, len(seperations)):
                    if amount > seperations[cnt - 1] and amount <= seperations[cnt]:
                        total_buy_amount_by_section_amount[str(seperations[cnt])] += amount
                        total_buy_by_amount_by_section_amount[str(seperations[cnt])] += amount * trade.price
                        break
            else:
                num_of_selling_transactions += 1
                accumulated_selling_amount += trade.amount
                accumulated_selling_price += trade.amount * trade.price
                amount = trade.amount
                for cnt in range(1, len(seperations)):
                    if amount > seperations[cnt - 1] and amount <= seperations[cnt]:
                        total_sell_amount_by_section_amount[str(seperations[cnt])] += amount
                        total_sell_by_amount_by_section_amount[str(seperations[cnt])] += amount * trade.price
                        break

        avg_price_by_amount = accumulated_price / total_amount
        avg_buy_by_amount = accumulated_buying_price / accumulated_buying_amount
        avg_sell_by_amount = accumulated_selling_price / accumulated_selling_amount
        buying_amount = accumulated_buying_amount
        selling_amount = accumulated_selling_amount
        avg_amount_by_transaction = total_amount / len(trades.trades)
        avg_price_gap_adjusted_by_volume = avg_buy_by_amount - avg_sell_by_amount

        for cnt in range(1, len(seperations)):
            if total_buy_amount_by_section_amount[str(seperations[cnt])] != 0:
                avg_buy_by_section_amount[str(seperations[cnt])] = total_buy_by_amount_by_section_amount[
                                                                       str(seperations[cnt])] / \
                                                                   total_buy_amount_by_section_amount[
                                                                       str(seperations[cnt])]
            if total_sell_amount_by_section_amount[str(seperations[cnt])] != 0:
                avg_sell_by_section_amount[str(seperations[cnt])] = total_sell_by_amount_by_section_amount[
                                                                        str(seperations[cnt])] / \
                                                                    total_sell_amount_by_section_amount[
                                                                        str(seperations[cnt])]
        result = {
            'avg_price_by_amount': avg_price_by_amount,
            'avg_buy_by_amount': avg_buy_by_amount,
            'avg_sell_by_amount': avg_sell_by_amount,
            'total_amount': total_amount,
            'buying_amount': buying_amount,
            'selling_amount': selling_amount,
            'avg_amount_by_transaction': avg_amount_by_transaction,
            'avg_amount_per_second': total_amount / timespan,
            'avg_price_gap_adjusted_by_volume': avg_price_gap_adjusted_by_volume,
            'timespan': timespan,
            'total_buy_amount_by_section_amount': total_buy_amount_by_section_amount,
            'total_sell_amount_by_section_amount': total_sell_amount_by_section_amount,
            'avg_buy_by_section_amount': avg_buy_by_section_amount,
            'avg_sell_by_section_amount': avg_sell_by_section_amount
        }
        return result

    def __init__(self, market, currency_pair, result, status=2, user_id=None, order_type=None):
        self.market = market
        self.currency_pair = currency_pair
        self.trades = []
        market = str(market).lower()
        try:
            if market == "okex":
                result = list(result)
                for item in result:
                    if item["type"] == "buy":
                        trade_type = 1
                    else:
                        trade_type = 0
                    trade = TradeInfo(item["date"], item["price"], item["amount"], trade_type, item["tid"], status)
                    self.trades.append(trade)
                self.message = "操作成功"
            if market == "aex":
                result = json.loads(result)
                for item in result:
                    if str(item["type"]) == 'buy':
                        trade_type = 1
                    else:
                        trade_type = 0
                    price = float(item['price'])
                    amount = float(item['amount'])
                    date = item['date']
                    tid = int(item['tid'])
                    trade = TradeInfo(date, price, amount, trade_type, tid, status)
                    self.trades.append(trade)
                self.message = "操作成功"
                self.trades.reverse()
            if market == "digifinex":
                result = json.loads(result)['data']
                for item in result:
                    if str(item["type"]) == 'buy':
                        trade_type = 1
                    else:
                        trade_type = 0
                    price = float(item['price'])
                    amount = float(item['amount'])
                    date = item['date']
                    tid = int(item['id'])
                    trade = TradeInfo(date, price, amount, trade_type, tid, status)
                    self.trades.append(trade)
                self.message = "操作成功"
                # self.trades.reverse()
            if market == 'kraken':
                if result is None:
                    return
                result = json.loads(result)['result']['XXBTZUSD']
                for item in result:
                    price = item[0]
                    amount = item[1]
                    date = item[2]
                    tid = None
                    if item[3] == 'b':
                        trade_type = 1
                    else:
                        trade_type = 0
                    status = 2
                    if order_type is None:
                        trade = TradeInfo(date, price, amount, trade_type, tid, status)
                        self.trades.append(trade)
                    if order_type == item[4]:
                        trade = TradeInfo(date, price, amount, trade_type, tid, status)
                        self.trades.append(trade)
                    else:
                        pass
                self.trades.reverse()
                self.message = "操作成功"
            if market == 'liquid':
                if result is None:
                    return
                result = json.loads(result)
                result = sorted(result, key=lambda x: x['id'])
                for item in result:
                    price = item['price']
                    amount = item['quantity']
                    date = item['created_at']
                    tid = item['id']
                    if item['taker_side'] == 'buy':
                        trade_type = 1
                    else:
                        trade_type = 0
                    status = 2
                    trade = TradeInfo(date, price, amount, trade_type, tid, status)
                    self.trades.append(trade)
                self.trades.reverse()
                self.message = "操作成功"
            if market == 'binance':
                if result is None:
                    return
                result = json.loads(result)
                result = sorted(result, key=lambda x: x['id'])
                for item in result:
                    price = item['price']
                    amount = item['qty']
                    date = item['time']
                    tid = item['id']
                    if item['isBuyerMaker'] == True:
                        trade_type = 0
                    else:
                        trade_type = 1
                    status = 2
                    trade = TradeInfo(date, price, amount, trade_type, tid, status)
                    self.trades.append(trade)
                self.message = "操作成功"
        except Exception as e:
            self.message = e
            print(e)


class BalanceInfo:
    '''
                :timestamp, :market, :total_asset, :net_asset, :free_cny,:free_btc,:frozen_btc,:free_ltc,:free_bcc,:free_eth,:free_etc,:free_bts,:free_hsr,
                :free_eos,:frozen_cny,:frozen_ltc,:frozen_bcc,:frozen_eth,:frozen_etc,:frozen_bts,:frozen_hsr,:frozen_eos,
                :free_usdt, :frozen_usdt, :free_bch, :frozen_bch, :free_btg, :frozen_btg, :free_gas , :frozen_gas, :free_zec , :frozen_zec, :free_neo , :frozen_neo,
                :free_iota , :frozen_iota, :free_gnt , :frozen_gnt, :free_snt , :frozen_snt, :free_dash , :frozen_dash , :free_xuc , :frozen_xuc, :free_qtum , :frozen_qtum,
                :free_omg , :frozen_omg,
                :message
    this is bewildering....
    fuck that....
    BalanceInfo class should have the following data members:
    1. timestamp
    2. market
    3. total_asset
    4. net_asset
    5. free
    6. frozen
    7. message
    '''

    def __init__(self, market, result):
        self.timestamp = int(time.time())
        self.market = market
        self.free = {}
        self.frozen = {}
        market = str(market).lower()
        try:
            if market == "okex":
                result = json.loads(result)
                if result["result"] == True:
                    self.message = "操作成功"
                    self.free = result["info"]["funds"]["free"]
                    self.free.pop("bcc")
                    self.frozen = result["info"]["funds"]["freezed"]
                    self.frozen.pop("bcc")
                else:
                    self.message = error_code.Error_code_for_OKEx[dict(result)["error_code"]]
            if market == "digifinex":
                result = json.loads(result)
                if result["code"] == 0:
                    self.message = "操作成功"
                    self.free = result["free"]
                    self.frozen = result["frozen"]
                else:
                    self.message = error_code.Error_code_for_DigiFinex[result["code"]]
            if market == "aex":
                if len(result) > 0:
                    self.message = "操作成功"
                    for key in result.keys():
                        if str(key).endswith('_lock'):
                            self.frozen[key] = result[key]
                        else:
                            self.free[key] = result[key]
                else:
                    self.message = error_code.Error_code_for_OKEx[dict(result)["error_code"]]
        except Exception as e:
            self.message = e
            print(e)


class CurrencyPairInfos:
    def __init__(self, market, result):
        # currency_pair, amount_precision, price_precision, minimum_amount=None, minimum_money=None
        market = str(market).lower()
        if market == 'digifinex':
            self.currency_pair_infos = {}
            result = json.loads(result)
            if result['code'] == 0:
                data = result['data']
                for key in data.keys():
                    __currencies = str(key).split('_')
                    currency_pair = CP.CurrencyPair(__currencies[1], __currencies[0])
                    amount_precision = data[key][0]
                    price_precision = data[key][1]
                    minimum_amount = data[key][2]
                    minimum_money = data[key][3]
                    currency_pair_info = CurrencyPairInfo(currency_pair, amount_precision, price_precision,
                                                          minimum_amount, minimum_money)
                    self.currency_pair_infos[currency_pair.toString()] = currency_pair_info
                self.message = '操作成功'
            else:
                self.message = error_code.Error_code_for_DigiFinex[result['code']]
        if market == 'kraken':
            self.currency_pair_infos = {}
            if len(result['error']) > 0:
                self.message = result['error'][0]
            else:
                data = result['result']
                for key in data.keys():
                    currency_pair = CP.CurrencyPair(data[key]['base'], data[key]['quote'])
                    amount_precision = data[key]['lot_decimals']
                    price_precision = data[key]['pair_decimals']
                    currency_pair_info = CurrencyPairInfo(currency_pair, amount_precision, price_precision)
                    self.currency_pair_infos[currency_pair.toString()] = currency_pair_info
                self.message = '操作成功'


class CurrencyPairInfo:
    '''
    message:

    currency_pair: of CurrencyPair
    amount_precision: 数量精度
    price_precision: 价格精度
    minimum_amount: 最小下单数量
    minimum_money: 最小下单金额
    '''

    def __init__(self, currency_pair, amount_precision, price_precision, minimum_amount=None, minimum_money=None):
        self.currency_pair = currency_pair
        self.amount_precision = amount_precision
        self.price_precision = price_precision
        self.minimum_amount = minimum_amount
        self.minimum_money = minimum_money
