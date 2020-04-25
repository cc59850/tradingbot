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


# # 取出各个子对象
# depths=data['depths']
# resistances=data['resistances']
# supports=data['supports']
# print('读取数据用时：',time.time()-t0)
#
# # 第一级预处理，试图把depths、resistances和supports变换成ndarray的形式
# temp_depths=[]
# for key in sorted(depths.keys()):
#     temp_depths.append(np.array(depths[key]))
#
# plot_resistances_and_supports(resistances,supports)
#
# total_length=len(depths['KrakenRest'])
# # total_length=3000
# resistances=resistances[:total_length]
# supports=supports[:total_length]
# processed_depths={}
# keys=sorted(depths.keys())
# for key in keys:
#     processed_depths[key]=[]
#
# # 仍然是预处理，把各个交易所的数据按照kranken的买卖一重新标准化一下
# t1=time.time()
# for cnt in range(0,total_length):
#     # 得到基准价格
#     base_price=get_base_price(temp_depths[10][cnt])
#     # 计算支撑阻力离base_price的距离
#     try:
#         resistances[cnt]=(resistances[cnt]-base_price)/100
#     except:
#         resistances[cnt]=0
#     try:
#         supports[cnt]=(supports[cnt]-base_price)/100
#     except:
#         supports[cnt]=0
#     # 分别计算每个交易所的100元档位的新深度图
#     # for key in keys:
#     t0=time.time()
#     length_of_temp_depths=len(temp_depths)
#     for cnt2 in range(0,length_of_temp_depths):
#         # print('正在处理',key,'的数据，使其变成100档的深度图，并ndarray化')
#         temp_depth=temp_depths[cnt2][cnt]
#         temp_depth=preprocess_depth(base_price,temp_depth)
#         temp_depth['asks'].reverse()
#         # whole_depth_snapshot是把买卖盘拼接起来的新的快照
#         whole_depth_snapshot=temp_depth['asks']+temp_depth['bids']
#         whole_depth_snapshot=np.array(whole_depth_snapshot)
#         processed_depths[keys[cnt2]].append(whole_depth_snapshot)
#     # print('处理16个交易所的100元档位深度用时',time.time()-t0)
# print('处理n条100元档位深度用时',time.time()-t1)
#
# # 对于一维回归，先把processed_depths拉成一个shape形如(n,1)的数组，再进行处理
# processed_depths2=[]
# for cnt in range(0,total_length):
#     for key in sorted(depths.keys()):
#         temp_depth = utils.normalize(processed_depths[key][cnt])
#         if key=='Binance':
#             temp_depths=temp_depth
#         else:
#             temp_depths= np.hstack((temp_depths,temp_depth))
#     processed_depths2.append(temp_depths)
# processed_depths2=np.array(processed_depths2)


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
