import keras
import numpy as np
from keras.models import Sequential
from keras.layers import Dense,Activation
from keras.optimizers import RMSprop
from keras_radam import RAdam
import matplotlib.pyplot as plt
import random
import utils
# 生成数据
dimensions=100
sample_numbers=2000
iterations=10000
X_series=[]
for cnt in range(dimensions):
    X_=np.random.random((sample_numbers,1))
    X_ = utils.normalize(X_)
    X_series.append(X_)

X_series=tuple(X_series)
X=np.hstack(X_series)
XX=[]
Y=np.zeros((sample_numbers,1),dtype=np.float)
for cnt in range(dimensions):
    XX_=X_series[cnt]*(np.sqrt(dimensions))
    Y=Y+XX_
Y=utils.normalize(Y)

# Y=Y+np.random.normal(0,0.05,(2000,1))

# 分配数据到不同的集合
_num=int(sample_numbers*0.8)
X_train=X[:_num]
X_test=X[_num:]
Y_train=Y[:_num]
Y_test=Y[_num:]

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

models['sgd']=model0
models['Adagrad']=model1
models['Adam']=model2
models['Adamax']=model3
models['Adadelta']=model4
models['Adagrad']=model5
models['RMSprop']=model6
models['Nadam']=model7
models['Radam']=model8

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
