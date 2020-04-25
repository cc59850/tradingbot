#python
import json
from urllib import parse
import requests
import time

class Forex():
    def __init__(self, api_key, sign, base_url):
        self.api_key=api_key
        self.sign=sign
        self.base_url=base_url

    def rate(self, base, reference, timestamp):
        ta=time.gmtime(timestamp)
        str_time=time.strftime('%Y%m%d',ta)

        params = {
            'app': 'finance.rate_unionpayintl',
            'cur_base': reference,
            'cur_transaction': base,
            'cur_date': str_time,
            'appkey': self.api_key,
            'sign': self.sign,
            'format': 'json',
        }
        params = parse.urlencode(params)
        result = requests.get('%s?%s' % (self.base_url, params))
        if result.status_code==200:
            result=json.loads(result.text)
            return result['result']['exchange_rate']
        else:
            return 'Error'

    def rate(self):
        pass

# test
if __name__=='__main__':
    forex=Forex('45452','91adb4e0e222cbdb9a55951ce00f8077','http://api.k780.com')
    print(forex.rate('JPY','USD',1568995200))