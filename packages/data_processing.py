import time
import pickle
import numpy as np
import utils

def get_base_price(depth):
    asks=depth['asks']
    bids=depth['bids']
    bid0 = bids[0][0]
    ask0 = asks[0][0]
    base_price = (bid0 + ask0) / 2
    base_price = int(base_price) + 1
    return base_price

def preprocess_depth(base_price, depth):
    '''
    # 加工数据
    # 假定：
    # 0. 基准价格为 base_price=(bid0+ask0)/2
    # 1. 未来n秒内触及到的高点不会超过 base_price+delta, 其中delta应该是通过统计求出的一个值，同时低点不会低于 base_price-delta, 暂定delta=100
    # 2. 将bidses和askses里面的每个元素进行变换， 保留 base_price ± 2*delta 之内的数据，之外的数据丢弃
    # 3. 采用离散编码重新表示bidses、askses和要预测的价格：
    #    3.1. 一元一档重新生成深度表，对原来的挂单数量进行合并
    #    3.2. 一元一档重新表示支撑和阻力
    # 4. 存在的问题：
    #    4.1.
    :param base_price:
    :param bids:
    :param asks:
    :param resistance:
    :return:
    '''
    # 生成一个depth，其中买1=原始买1.floor，卖一=买一+1，然后逐一向上下延伸100个档位，每个档位相隔1元
    asks=depth['asks']
    bids=depth['bids']
    new_bids=[]
    new_asks=[]

    # 确定新的买卖1的位置，记为bid0，ask0
    bid0=int(base_price)+25
    ask0=int(base_price)-25

    # 重构整个订单簿
    for n in range(0,100):
        bid_price_lower_bound=bid0-n
        amount=0
        for b in bids:
            if b[0]>bid_price_lower_bound and b[0]<=bid_price_lower_bound+1:
                amount+=b[1]
        new_bids.append(amount)
    for n in range(0,100):
        ask_price_upper_bound=ask0+n
        amount=0
        for a in asks:
            if a[0]<=ask_price_upper_bound and a[0]>ask_price_upper_bound-1:
                amount+=a[1]
        new_asks.append(amount)

    result = {
        'bids': new_bids,
        'asks': new_asks,
    }
    return result

def read_file(file_path):
    # 从文件读取对象
    t0 = time.time()
    file = open(file_path, 'rb')
    data = pickle.load(file)
    file.close()

    # 取出各个子对象
    depths = data['depths']
    resistances = data['resistances']
    supports = data['supports']
    print('读取数据用时：', time.time() - t0)

    return (depths,resistances,supports)

def to_ndarray(data):
    result=np.array(data)
    return result

def get_statistics(data):
    mean=np.mean(data,axis=0)
    std=np.std(data, axis=0)
    return {
        "mean":mean,
        "std":std
    }

def to_norm(data, mean, std):
    return (data-mean)/std

def read_data_from_db(conn):
    '''
    从数据库读文件，并返回一个ndarray
    :param conn:
    :return:
    '''
    from packages import db
    import CONSTANTS
    myPGManager=db.PGManager(**CONSTANTS.DB_CONNECT_ARGS_LOCAL)


def process_data(depths, supports, resistances):
    # 第一级预处理，试图把depths、resistances和supports变换成ndarray的形式
    temp_depths = []
    for key in sorted(depths.keys()):
        temp_depths.append(np.array(depths[key]))
    total_length = len(depths['KrakenRest'])
    # total_length=3000
    resistances = resistances[:total_length]
    supports = supports[:total_length]
    processed_depths = {}
    keys = sorted(depths.keys())
    for key in keys:
        processed_depths[key] = []

    # 仍然是预处理，把各个交易所的数据按照kranken的买卖一重新标准化一下
    t1 = time.time()
    for cnt in range(0, total_length):
        # 得到基准价格
        base_price = get_base_price(temp_depths[10][cnt])
        # 计算支撑阻力离base_price的距离
        try:
            resistances[cnt] = (resistances[cnt] - base_price) / 1000
        except:
            resistances[cnt] = 0
        try:
            supports[cnt] = (supports[cnt] - base_price) / 1000
        except:
            supports[cnt] = 0
        # 分别计算每个交易所的100元档位的新深度图
        # for key in keys:
        t0 = time.time()
        length_of_temp_depths = len(temp_depths)
        for cnt2 in range(0, length_of_temp_depths):
            # print('正在处理',key,'的数据，使其变成100档的深度图，并ndarray化')
            temp_depth = temp_depths[cnt2][cnt]
            temp_depth = preprocess_depth(base_price, temp_depth)
            temp_depth['asks'].reverse()
            # whole_depth_snapshot是把买卖盘拼接起来的新的快照
            whole_depth_snapshot = temp_depth['asks'] + temp_depth['bids']
            whole_depth_snapshot = np.array(whole_depth_snapshot)
            processed_depths[keys[cnt2]].append(whole_depth_snapshot)
        # print('处理16个交易所的100元档位深度用时',time.time()-t0)
    print('处理n条100元档位深度用时', time.time() - t1)
    return (processed_depths,resistances,supports)

def to_one_dimension(processed_depths):
    t0=time.time()
    # 对于一维回归，先把processed_depths拉成一个shape形如(n,1)的数组，再进行处理
    processed_depths2 = []
    total_length=len(processed_depths['KrakenRest'])
    keys=sorted(processed_depths.keys())
    for cnt in range(0, total_length):
        for key in keys:
            temp_depth = utils.normalize(processed_depths[key][cnt])
            if key == 'Binance':
                temp_depths = temp_depth
            else:
                temp_depths = np.hstack((temp_depths, temp_depth))
        processed_depths2.append(temp_depths)
    processed_depths2 = np.array(processed_depths2)
    print('扁平化 ',total_length,' 条数据用时:',time.time()-t0)
    return processed_depths2

def restore_missing_values(data):

    # supports_and_resistances=[supports,resistances]
    previous = data[0]
    for cnt in range(1, len(data)):
        if data[cnt] is None:
            data[cnt] = previous
        else:
            previous = data[cnt]

def restore_data_from_norm(norm, statistics):
    mean=statistics['mean']
    std=statistics['std']
    data=norm*std+mean
    return data

if __name__=='__main__':
    for ts in range(1567267200,1567267200+1,86400):
        # -1. 确定文件名
        file_name='G:\\量化交易\\莫烦keras教程\\data\\data_'+str(ts)+'_2400'

        # 0. 从文件读取对象，并改写成ndarray的格式
        depths, resistances, supports=read_file(file_name)

        # 0.1 缺失值默认为前值
        restore_missing_values(resistances)
        restore_missing_values(supports)
        resistances=to_ndarray(resistances)
        supports=to_ndarray(supports)

        # 废弃不用--------------------------
        # 1. 按照kraken的买卖一基准价格重新标准化
        # processed_depths, resistances, supports=process_data(depths, resistances, supports)
        # 废弃不用--------------------------

        # 1.1 替代1，按照 array=(array-mean)/std进行正则化
        # 1.1.1 求出mean和std
        mean=max(get_statistics(resistances)['mean'],get_statistics(supports)['mean'])
        std=max(get_statistics(resistances)['std'],get_statistics(supports)['std'])
        statistics= {
            'mean':mean,
            'std':std
        }
        # 1.1.2 正则化
        resistances=to_norm(resistances, mean, std)
        supports=to_norm(supports, mean, std)
        # 1.1.2.1 数据恢复，测试用
        # resistances=restore_data_from_norm(resistances, statistics['resistances'])
        # supports=restore_data_from_norm(supports,statistics['supports'])

        # 2. 扁平化
        # flatten_depths=to_one_dimension(processed_depths)

        # 3. 将扁平化后的对象写入到文件中
        t0 = time.time()
        # file_name = 'flatten_' + str(ts)+'_60s'
        file_name = 'xxx_' + str(ts) + '_2400'
        file = open(file_name, 'wb')
        data={
            # 'flatten_depths':flatten_depths,
            'statistics': statistics,
            'resistances':resistances,
            'supports':supports
        }
        pickle.dump(data, file)
        file.close()
        print('处理数据用时：', time.time() - t0)
