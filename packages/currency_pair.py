import sys
sys.path.append("..")
class CurrencyPair:

    @classmethod
    def get_all_currency_pairs(cls, market, account=None, user_id=None):
        market=str(market).lower()
        if market=='digifinex':
            from packages import digifinex as DIGIFINEX
            digifinex=DIGIFINEX.DigiFinex(account)
            tickers=digifinex.ticker()
            # 在digiFinex返回的tickers数据结构里，每个项的vol字段的值指的是base的成交量，而不是reference的成交量，所以首先要变成reference成交量
            currency_pairs={
                'usdt':[],
                'btc':[],
                'usdt2':[],
                'eth':[],
                'dft':[]
            }
            # currency_pairs_in_reference_of_btc=[]
            # currency_pairs_in_reference_of_usdt = []
            # currency_pairs_in_reference_of_usdt2 = []
            # currency_pairs_in_reference_of_eth = []
            # currency_pairs_in_reference_of_dft = []
            for item in dict(tickers).keys():
                base=str(item).split('_')[1]
                reference=str(item).split('_')[0]
                currency_pair=CurrencyPair(base,reference)
                vol=tickers[item]['vol']*tickers[item]['last']
                currency_pairs[reference].append({
                    'currency_pair':currency_pair,
                    'vol':vol,
                    'reference':reference
                })
            #     sorted(x, key=lambda x : x['name'], reverse=True)
            for item in currency_pairs.keys():
                currency_pairs[item]=sorted(currency_pairs[item], key=lambda x : x['vol'], reverse=True)
        if market=='aex':
            from packages import aex as AEX
            aex=AEX.AEX(account, user_id)
            tickers={}
            tickers['cny']=aex.ticker(CurrencyPair('all','cny'),True)
            tickers['usdt']=aex.ticker(CurrencyPair('all','usdt'),True)
            # 在digiFinex返回的tickers数据结构里，每个项的vol字段的值指的是base的成交量，而不是reference的成交量，所以首先要变成reference成交量
            _tickers={}
            for key1 in tickers.keys():
                for key2 in tickers[key1]:
                    if key1+'_'+key2=='usdt_tusd' or key1+'_'+key2=='usdt_pax':
                        continue
                    _tickers[key1+'_'+key2]=tickers[key1][key2]['ticker']
            tickers=_tickers
            currency_pairs={
                'usdt':[],
                'cny':[]
            }
            for item in dict(tickers).keys():
                base=str(item).split('_')[1]
                reference=str(item).split('_')[0]
                currency_pair=CurrencyPair(base,reference)
                vol=tickers[item]['vol']*tickers[item]['last']
                currency_pairs[reference].append({
                    'currency_pair':currency_pair,
                    'vol':vol,
                    'reference':reference
                })
            #     sorted(x, key=lambda x : x['name'], reverse=True)
            for item in currency_pairs.keys():
                currency_pairs[item]=sorted(currency_pairs[item], key=lambda x : x['vol'], reverse=True)
        return currency_pairs

    @classmethod
    def get_top_n_currency_pairs_adjusted_by_vol(cls,market, account=None, top_n=5, user_id=None):
        currency_pairs=CurrencyPair.get_all_currency_pairs(market,account, user_id)
        for item in currency_pairs.keys():
            currency_pairs[item]=currency_pairs[item][:top_n]
        return currency_pairs

    @classmethod
    def find_triangle_arbitragable_currency_pairs(cls,market, account=None, top_n=5, user_id=None):
        currency_pairs=CurrencyPair.get_top_n_currency_pairs_adjusted_by_vol(market,account,top_n, user_id)
        arbitragable_keypairs=[]
        _currency_pairs=[]
        for item in currency_pairs.keys():
            for item2 in currency_pairs[item]:
                _currency_pairs.append(item2['currency_pair'])
        for i in range(0,len(_currency_pairs)):
            cp1=_currency_pairs[i]
            for j in range(i+1,len(_currency_pairs)):
                cp2=_currency_pairs[j]
                for k in range(j+1,len(_currency_pairs)):
                    cp3=_currency_pairs[k]
                    currencies=[]
                    currencies.append(cp1.base)
                    currencies.append(cp1.reference)
                    currencies.append(cp2.base)
                    currencies.append(cp2.reference)
                    currencies.append(cp3.base)
                    currencies.append(cp3.reference)
                    distinctive_currencies=list(set(currencies))
                    if currencies.count(distinctive_currencies[0])==2 and currencies.count(distinctive_currencies[1])==2 and currencies.count(distinctive_currencies[2])==2:
                        arbitragable_keypairs.append([cp1,cp2,cp3])

        a=1
        return arbitragable_keypairs


    def __init__(self,base='btc', reference='usdt'):
        self.base=base
        self.reference=reference

    def subtract(self, other):
        if other==self.base:
            return self.reference
        if other==self.reference:
            return self.base
        else:
            return None

    def equals(self, other):
        if self.base==other.base and self.reference==other.reference:
            return True
        else:
            return False

    def contains(self, currency):
        if self.base==currency or self.reference==currency:
            return True
        else:
            return False

    def toString(self):
        return self.base+'_'+self.reference

    def get_currency_pair(self):
        return self.base+'_'+self.reference

    def get_referencial_currencies(self, market):
        market=str(market).lower()
        if market=="okex":
            return ["btc","usdt","eth","bch"]
        elif market=="chbtc" or market=="zb":
            pass
        elif market=="???":
            pass
        else:
            pass

    def get_referencial_currency(self, string):
        try:
            reference=str(string).split("_")[1]
        except Exception as e:
            reference=None
        return reference

    def get_base_currency(self, string):
        try:
            reference=str(string).split("_")[0]
        except Exception as e:
            reference=None
        return reference

class Currency:

    def __init__(self, name):
        self.name=name