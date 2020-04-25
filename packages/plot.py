import matplotlib.pyplot as plt
import mpl_finance as mpf
import numpy as np
import numpy as np


class Cursor(object):
    def __init__(self, ax):
        self.ax = ax
        self.lx = ax.axhline(color='k')  # the horiz line
        self.ly = ax.axvline(color='k')  # the vert line

        # text location in axes coords
        self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

    def mouse_move(self, event):
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)

        self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
        plt.draw()


class SnaptoCursor(object):
    """
    Like Cursor but the crosshair snaps to the nearest x,y point
    For simplicity, I'm assuming x is sorted
    """

    def __init__(self, ax, x, y):
        self.ax = ax
        self.lx = ax.axhline(color='k')  # the horiz line
        self.ly = ax.axvline(color='k')  # the vert line
        self.x = x
        self.y = y
        # text location in axes coords
        self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

    def mouse_move(self, event):

        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata

        indx = min(np.searchsorted(self.x, [x])[0], len(self.x) - 1)
        x = self.x[indx]
        y = self.y[indx]
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)

        self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
        print('x=%1.2f, y=%1.2f' % (x, y))
        plt.draw()

def plot_resistances_and_supports(resistances, supports):
    '''
    画图模块：根据支撑阻力位画出一个二维平面图
    :param resistances:
    :param supports:
    :return:
    '''
    sample_numbers = len(resistances)
    resistances = resistances[:sample_numbers]
    supports = supports[:sample_numbers]
    x_axis = np.arange(0, sample_numbers)

    plt.figure(facecolor='white', figsize=(32, 18))
    plt.plot(x_axis, supports, c='green', linewidth=0.5)
    plt.plot(x_axis, resistances, c='red', linewidth=0.5)
    plt.show()


def plot_Klines(klines, auto_xaxis=True):
    import datetime
    from matplotlib.pylab import date2num
    alist = []
    vols_bid = []
    vols_ask = []
    diff_bid_2_ask = []
    diff_bid_2_ask_in_past_2_epochs = []
    diff_bid_2_ask_in_past_3_epochs = []
    dates = []
    cnt = 0
    date = date2num(datetime.datetime.fromtimestamp(klines.klines[0].timestamp))
    # for kline in klines.klines:
    for cnt in range(2, len(klines.klines)):
        kline_previous2 = klines.klines[cnt - 2]
        kline_previous1 = klines.klines[cnt - 1]
        kline = klines.klines[cnt]
        date = date + 1 if auto_xaxis == True else date
        data = (date, kline.open, kline.high, kline.low, kline.close)
        alist.append(data)
        vols_bid.append(-kline.vol_bid)
        vols_ask.append(kline.vol_ask)
        diff_bid_2_ask.append(kline.vol_bid - kline.vol_ask)
        diff_bid_2_ask_in_past_2_epochs.append(
            kline.vol_bid + kline_previous1.vol_bid - kline.vol_ask - kline_previous1.vol_ask)
        diff_bid_2_ask_in_past_3_epochs.append(
            kline.vol_bid + kline_previous1.vol_bid + kline_previous2.vol_bid - kline.vol_ask - kline_previous1.vol_ask - kline_previous2.vol_ask)
        dates.append(date)

    # fig, ax = plt.subplots(figsize=(32, 18))
    # fig.subplots_adjust(bottom=0.5)
    # mpf.candlestick_ohlc(ax, alist, width=0.5, colorup='g', colordown='r', alpha=1.0)
    # plt.grid(True)
    # # 设置日期刻度旋转的角度
    # plt.xticks(rotation=30)
    # plt.title('wanda yuanxian 17')
    # plt.xlabel('Date')
    # plt.ylabel('Price')
    # # x轴的刻度为日期
    # ax.xaxis_date()

    fig, (ax1, ax2) = plt.subplots(2, sharex=True, figsize=(32, 15))
    mpf.candlestick_ohlc(ax1, alist, width=0.5, colorup='g', colordown='r')
    ax1.set_title('BTC')
    ax1.set_ylabel('价格')
    ax1.grid(True)
    ax1.xaxis_date()
    # plt.bar(dates , vols_ask, width=0.5)
    # plt.bar(dates, vols_bid, width=0.5)
    plt.plot(dates, diff_bid_2_ask, c='green',linewidth=0.2)
    plt.plot(dates, diff_bid_2_ask_in_past_2_epochs, c='orange',linewidth=0.2)
    plt.plot(dates, diff_bid_2_ask_in_past_3_epochs, c='blue',linewidth=0.2)
    ax2.set_ylabel('成交量')
    ax2.grid(True)
    plt.show()


def plot_lists(lists):
    pass
