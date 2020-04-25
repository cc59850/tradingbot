'''
作者：纽润量化团队
问题分析：
    比特币未来一段时间（也可以是别的周期，比如成交量周期、成交笔数周期、大事件周期）的高低点，在此例中是阻力和支撑点，记为(Resistance, Support)
    比特币当前的数据，包括：
        0. 各大交易所的深度快照数据，记为Depths=(depth0,depth1,depth2...,depthn)，
        1. 历史成交记录，即tick数据，记为trades=(trade0,trade1...traden)
        2. 多个交易所的成交记录的聚合，记为tradeses=(trades0,trades1...tradesn)
        3. K线数据，记为Klines，在有效市场中，通常K线是高度一致的，不同的比特币-法币交易对可能唯一存在的不一致性出自法币1-法币2的汇率波动
        4. others,其他数据，比如比特币供应总量，前一周期的数据等
    所以(Resistance, Supports)=F(Depths,tradeses,Klines,others)
    问题就是求出F，及resistance、support
    根据过往经验，预测未来某个周期内的价格高低点，主要是盯住深度表，也可能需要考虑成交量，然后算深度表的积累深度，但是这个过程难以对多个
    同级别的深度表进行并行计算，因为无法确定每个深度表的权重。

    若干问题：
    0. 深度如何标准化？
    问题分析：每个交易所拿刀的深度基本是同一个时间点的，但每个交易所的比特币交易对可能不一样，例如，有的交易所是"比特币-人民币"，
    有的交易所是"比特币-美元"，有的是"比特币-日元"，我们是否应该将所有的交易对标准化？

'''

import keras
import matplotlib.pyplot as plt
import numpy as np
from keras.layers import Dense,Dropout
from keras.models import Sequential
from keras_radam import RAdam
import pickle
import time


def plot_resistances_and_supports(resistances, supports):
    '''
    画图模块：根据支撑阻力位画出一个二维平面图
    :param resistances:
    :param supports:
    :return:
    '''
    sample_numbers=len(resistances)
    resistances=resistances[:sample_numbers]
    supports=supports[:sample_numbers]
    x_axis=np.arange(0,sample_numbers)

    plt.plot(x_axis,supports,c='green', linewidth=0.5)
    plt.plot(x_axis, resistances, c='red', linewidth=0.5)
    plt.show()

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

# 从文件读取对象
t0=time.time()
file=open('data\\flatten_'+str(1567267200)+'_60s','rb')
data=pickle.load(file)
file.close()
flatten_depths=data['flatten_depths']
resistances=data['resistances']
supports=data['supports']

for ts in range(1567353600,1568131200+1,86400):
    file=open('data\\flatten_'+str(ts)+'_60s','rb')
    data=pickle.load(file)
    file.close()
    flatten_depths=np.vstack((flatten_depths,data['flatten_depths']))
    resistances.extend(data['resistances'])
    supports.extend(data['supports'])

X=flatten_depths
np_array_resistances=np.array(resistances)
np_array_supports=np.array(supports)
Y1=np_array_resistances
Y2=np_array_supports
plot_resistances_and_supports(resistances,supports)
dimensions=X.shape[1]
sample_numbers=X.shape[0]
iterations=100000

# 统计
avg_resistances=np.mean(np_array_resistances)
avg_supports=np.mean(np_array_supports)
std_supports=np.std(np_array_supports)
std_resistances=np.std(np_array_resistances)
a=1
# 分配数据到不同的集合
_num=int(sample_numbers*0.8)
X_train=X[:_num]
X_test=X[_num:]
Y_train=Y1[:_num]
Y_test=Y1[_num:]

# build several models of different types:
models={}

# build the nn
activation1=keras.layers.LeakyReLU(alpha=0.3)
dense1=Dense(input_dim=dimensions,units=1)

model0=Sequential()
dense1=Dense(input_dim=dimensions,units=1)
model0.add(dense1)
model0.compile(optimizer='sgd',loss='mse')

model1=Sequential()
dense1=Dense(input_dim=dimensions,units=1)
model1.add(dense1)
opt=keras.optimizers.Adagrad()
model1.compile(optimizer=opt,loss='mse')

model2=Sequential()
dense1=Dense(input_dim=dimensions,units=1)
model2.add(dense1)
opt=keras.optimizers.Adam()
model2.compile(optimizer=opt,loss='mse')

model3=Sequential()
dense1=Dense(input_dim=dimensions,units=1)
model3.add(dense1)
opt=keras.optimizers.Adamax()
model3.compile(optimizer=opt,loss='mse')

model4=Sequential()
dense1=Dense(input_dim=dimensions,units=1)
model4.add(dense1)
opt=keras.optimizers.Adadelta(lr=0.1)
model4.compile(optimizer=opt,loss='mse')

model5=Sequential()
dense1=Dense(input_dim=dimensions,units=1)
model5.add(dense1)
opt=keras.optimizers.Adagrad(lr=0.001)
model5.compile(optimizer=opt,loss='mse')

model6=Sequential()
dense1=Dense(input_dim=dimensions,units=1)
model6.add(dense1)
opt=keras.optimizers.RMSprop(lr=0.01,decay=0.01)
model6.compile(optimizer=opt,loss='mse')

model7=Sequential()
dense1=Dense(input_dim=dimensions,units=1)
model7.add(dense1)
opt=keras.optimizers.Nadam()
model7.compile(optimizer=opt,loss='mse')

model8=Sequential()
dense1=Dense(input_dim=dimensions,units=1)
model8.add(dense1)
opt=RAdam()
model8.compile(optimizer=opt,loss='mse')

# 非线性回归
activation=keras.layers.LeakyReLU(alpha=0.3)
# activation=keras.layers.Activation('tanh')
model9=Sequential()
model9.add(Dense(input_dim=dimensions,units=1000))
model9.add(Dropout(0.4))
model9.add(activation)
model9.add(Dense(300))
model9.add(Dropout(0.2))
model9.add(activation)
model9.add(Dense(100))
model9.add(Dropout(0.2))
model9.add(activation)
model9.add(Dense(30))
model9.add(Dropout(0.2))
model9.add(activation)
model9.add(Dropout(0.2))
model9.add(Dense(6))
model9.add(activation)
model9.add(Dense(1))
model9.add(activation)
import os
if os.path.exists('G:\\量化交易\\莫烦keras教程\\model.h5'):
    model9.load_weights('G:\\量化交易\\莫烦keras教程\\model.h5')
model9.compile(optimizer=opt,loss='mae')
# models['sgd']=model0
# models['Adagrad']=model1
# models['Adam']=model2
# models['Adamax']=model3
# models['Adadelta']=model4
# models['Adagrad']=model5
# models['RMSprop']=model6
# models['Nadam']=model7
# models['Radam']=model8

from keras.models import load_model

# models['Multi_Nonlinear']=model9
models['h5']=model9
costs={}

# iterate:
for key in models:
    model=models[key]
    costs[key]=[]
    # train
    print()
    print()
    print()
    print('==='*15)
    print('Training-----------------------------------')
    count=0
    import time
    t0=time.time()
    for step in range(iterations):
        cost=model.train_on_batch(X_train,Y_train)

        if step%50==0:
            cost_for_evaluation = model.evaluate(X_test, Y_test)
            costs[key].append(cost)
            print('Training cost:',cost,'  testing cost:',cost_for_evaluation)
        if cost<0.0005:
            count+=1
        if count==100:
            break
    t1 = time.time() - t0
    print(str(key) +  ' finds solution in ' + str(step) + ' whose cost is ' + str(cost) + '. Time used:' + str(t1))
    model.save_weights('model.h5')
    # predict
    Y_pred=model.predict(X_test)

    print('Testing------------------------------------')
    cost=model.evaluate(X_test,Y_test)
    print('Testing cost:',cost)

for key in costs:
    color='green'
    if key=='Adam':
        color='green'
    elif key=='Adamax':
        color='red'
    elif key=='Radam':
        color='yellow'
    ccs=costs[key]
    X_axis=np.arange(len(ccs))
    plt.scatter(x=X_axis,y=ccs,c=color,linewidths=0.1)
plt.show()
