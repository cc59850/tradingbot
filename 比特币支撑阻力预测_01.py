import keras
import matplotlib.pyplot as plt
import numpy as np
from keras.layers import Dense
from keras.models import Sequential
from keras_radam import RAdam
import math
import utils

# 读取数据
data=utils.read_data(duration=100000, forcasting_period=600)
bidses=data['bidss']
askses=data['askss']
resistances=data['resistances']
supports=data['supports']

def plot_resistances_and_supports(resistances, supports):
    sample_numbers=resistances.shape[0]
    resistances=resistances[:sample_numbers]
    supports=supports[:sample_numbers]
    x_axis=np.arange(0,sample_numbers)
    plt.scatter(x=x_axis,y=resistances,c='red')
    plt.scatter(x=x_axis,y=supports,c='green')
    plt.show()


plot_resistances_and_supports(resistances,supports)



def preprocess_data(base_price, bids, asks, resistance=None, support=None):
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

    new_bids=[]
    new_asks=[]
    if base_price is None:
        bid0=bids[0][0]
        ask0=asks[0][0]
        base_price=(bid0+ask0)/2
        bid0=int(base_price)+1
        ask0=bid0

    for n in range(0,100):
        bid_price_lower_bound=bid0-n
        amount=0
        for b in bids:
            if b[0]>bid_price_lower_bound and b[0]<=bid_price_lower_bound+1:
                amount+=b[1]
        new_bids.append(amount  )
    for n in range(0,100):
        ask_price_upper_bound=ask0+n
        amount=0
        for a in asks:
            if a[0]<=ask_price_upper_bound and a[0]>ask_price_upper_bound-1:
                amount+=a[1]
        new_asks.append(amount)

    # 处理支撑和阻力
    resistance=(float(resistance)-bid0)/100.0
    support=(float(support)-ask0)/100.0

    result = {
        'base_price': base_price,
        'bids': new_bids,
        'asks': new_asks,
        'resistance':resistance,
        'support':support
    }
    return result

processed_bidses=[]
processed_askses=[]
processed_supports=[]
processed_resistances=[]
rows_count=len(bidses)
for cnt in range(rows_count):
    bids=bidses[cnt]
    asks=askses[cnt]
    support=supports[cnt]
    resistance=resistances[cnt]
    result=preprocess_data(None,bids,asks,resistance,support)
    # 加入到一个序列中
    processed_askses.append(result['asks'])
    processed_bidses.append(result['bids'])
    processed_resistances.append(result['resistance'])
    processed_supports.append(result['support'])
    a=1

np_array_askses=utils.normalize(np.array(processed_askses))
np_array_bidses=utils.normalize(np.array(processed_bidses))
np_array_resistances=np.array(processed_resistances)
np_array_supports=np.array(processed_supports)
X=np.hstack((np_array_askses,np_array_bidses))
Y1=np_array_resistances
Y2=np_array_supports

dimensions=X.shape[1]
sample_numbers=X.shape[0]
iterations=50000
# X_series=[]
# for cnt in range(dimensions):
#     X_=np.random.random((sample_numbers,1))
#     X_ = utils.normalize(X_)
#     X_series.append(X_)
#
# X_series=tuple(X_series)
# X=np.hstack(X_series)
# XX=[]
# Y=np.zeros((sample_numbers,1),dtype=np.float)
# for cnt in range(dimensions):
#     XX_=X_series[cnt]*(np.sqrt(dimensions))
#     Y=Y+XX_
# Y=utils.normalize(Y)

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
model9=Sequential()
model9.add(Dense(input_dim=dimensions,units=100))
model9.add(activation)
model9.add(Dense(37))
model9.add(activation)
model9.add(Dense(5))
model9.add(activation)
model9.add(Dense(1))
model9.add(activation)
model9.compile(optimizer=opt,loss='mse')
# models['sgd']=model0
# models['Adagrad']=model1
# models['Adam']=model2
# models['Adamax']=model3
# models['Adadelta']=model4
# models['Adagrad']=model5
# models['RMSprop']=model6
# models['Nadam']=model7
# models['Radam']=model8
models['Multi_Nonlinear']=model9
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
            costs[key].append(cost)
            print(cost)
        if cost<0.000001:
            count+=1
        if count==10:
            break
    t1 = time.time() - t0
    print(str(key) +  ' finds solution in ' + str(step) + ' whose cost is ' + str(cost) + '. Time used:' + str(t1))
    # predict
    Y_pred=model.predict(X_test)

    print('Testing------------------------------------')
    cost=model.evaluate(X_test,Y_test,batch_size=400)
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
