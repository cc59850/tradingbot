from packages import db as DB
import CONSTANTS
from packages import universal as UNIVERSAL
import numpy as np
import pandas as pd


class Data():
    @staticmethod
    def from_db(query='select * from trades_for_kraken order by timestamp desc'):
        pgmanager = DB.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)
        trades = pgmanager.select(query)
        return trades

    @staticmethod
    def to_db(klines, tablename, normalize=False):
        pgmanager = DB.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)
        sqls = []

        if normalize:
            pass

        if klines.klines[0].__class__ == UNIVERSAL.Kline:
            for kline in klines.klines:
                param = {
                    'timestamp': kline.timestamp,
                    'open': kline.open,
                    'high': kline.high,
                    'low': kline.low,
                    'close': kline.close,
                    'volume': kline.vol
                }
                sqls.append(param)
            pgmanager.execute_many(
                'insert into ' + tablename + '(timestamp,o,h,l,c,vol) values(%(timestamp)s,%(open)s,%(high)s,%(low)s,%(close)s,%(volume)s)',
                sqls)
        if klines.klines[0].__class__ == UNIVERSAL.KlineWithVol:
            for kline in klines.klines:
                param = {
                    'timestamp': kline.timestamp,
                    'open': kline.open,
                    'high': kline.high,
                    'low': kline.low,
                    'close': kline.close,
                    'volume': kline.vol,
                    'vol_buy': kline.vol_bid,
                    'vol_sell': kline.vol_ask,
                    'avg_buy': kline.avg_buy,
                    'avg_sell': kline.avg_sell,
                    'avg_amount': kline.avg_amount_per_trade
                }
                sqls.append(param)
            pgmanager.execute_many(
                'insert into ' + tablename + '(timestamp,o,h,l,c,vol,vol_buy,vol_sell,avg_buy,avg_sell,avg_amount_per_trade) values'
                                             '(%(timestamp)s,%(open)s,%(high)s,%(low)s,'
                                             '%(close)s,%(volume)s,%(vol_buy)s,%(vol_sell)s,'
                                             '%(avg_buy)s,%(avg_sell)s,%(avg_amount)s)', sqls)

    def __init__(self, filename, split, cols, preprocessing_method="standardize"):
        dataframe = pd.read_csv(filename)
        upperbound = min(250000, len(dataframe))
        length=len(dataframe)
        i_split = int(upperbound * split)
        data = dataframe.get(cols).values[length-upperbound:]
        self.maxes = np.max(data, axis=0)
        self.mins = np.min(data, axis=0)
        self.means = np.mean(data, axis=0)
        self.deltas = np.std(data, axis=0)

        self.data_train = data[:i_split, :]
        self.data_test = data[i_split:, :]
        self.len_train = len(self.data_train)
        if preprocessing_method == "normalize":
            self.normalize()
        if preprocessing_method == "standardize":
            self.standardize()

    def restore(self, data, method="normalize"):
        if method == "normalize":
            return data * (self.maxes[-1] - self.mins[-1]) + self.mins[-1]
        else:
            return data * self.deltas[-1] + self.means[-1]

    def normalize(self):
        col_len = self.data_train.shape[1]
        for i in range(0, col_len):
            self.data_train[:, i] = (self.data_train[:, i] - self.mins[i]) / (self.maxes[i] - self.mins[i])
            self.data_test[:, i] = (self.data_test[:, i] - self.mins[i]) / (self.maxes[i] - self.mins[i])

    def standardize(self):
        col_len = self.data_train.shape[1]

        for i in range(0, col_len):
            self.data_train[:, i] = (self.data_train[:, i] - self.means[i]) / self.deltas[i]
            self.data_test[:, i] = (self.data_test[:, i] - self.means[i]) / self.deltas[i]

    def get_train_data(self, length=1000, target_col=-1):
        '''
        Create x, y train data windows
        Warning: batch method, not generative, make sure you have enough memory to
        load data, otherwise use generate_training_window() method.
        '''
        col_lenth = self.data_train.shape[1]
        row_length = self.data_train.shape[0]
        data_x = []
        data_y = []
        for i in range(0, row_length - length):
            x = self.data_train[i:i + length, :col_lenth - 1]
            y = self.data_train[i + length-1, target_col]
            data_x.append(x)
            data_y.append(y)
        data_x = np.array(data_x)
        data_y = np.array(data_y)
        # data_x = data_x.reshape(data_x.shape[0], data_x.shape[1], data_x.shape[2], 1)
        return data_x, data_y

    def get_test_data(self, length=1000, target_col=-1):
        '''
        Create x, y test data windows
        Warning: batch method, not generative, make sure you have enough memory to
        load data, otherwise reduce size of the training split.
        '''
        col_lenth = self.data_test.shape[1]
        row_length = self.data_test.shape[0]
        data_x = []
        data_y = []
        for i in range(0, row_length - length):
            x = self.data_test[i:i + length, :col_lenth - 1]
            y = self.data_test[i + length-1, target_col]
            data_x.append(x)
            data_y.append(y)
        data_x = np.array(data_x)
        data_y = np.array(data_y)
        # data_x = data_x.reshape(data_x.shape[0], data_x.shape[1], data_x.shape[2], 1)
        return data_x, data_y

    def generate_train_batch(self, batch_size, length=1000, target_col=-1):
        '''Yield a generator of training data from filename on given list of cols split for train/test'''
        i = 0

        while i < self.len_train-length:
            col_lenth = self.data_train.shape[1]
            row_length = self.data_train.shape[0]
            x_batch = []
            y_batch = []
            for b in range(batch_size):
                x = self.data_train[i:i + length, :col_lenth - 1]
                y = self.data_train[i + length - 1, target_col]
                x_batch.append(x)
                y_batch.append(y)
                i+=1
            # data_x = data_x.reshape(data_x.shape[0], data_x.shape[1], data_x.shape[2], 1)
            yield x_batch, y_batch

