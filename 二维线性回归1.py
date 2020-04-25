import numpy as np
from keras.models import Sequential
from keras.layers import Dense,Activation
from keras.optimizers import RMSprop
import matplotlib.pyplot as plt

# 生成数据
X1=np.random.random((2000,1))
X2=np.random.random((2000,1))
X=np.hstack((X1,X2))
print(X[:10])
XX1=0.5*X1
XX2=1.4*X2
Y=XX1+XX2+2
# Y=Y+np.random.normal(0,0.05,(2000,1))

# 分配数据到不同的集合
X_train=X[:1600]
X_test=X[1600:]
Y_train=Y[:1600]
Y_test=Y[1600:]

# build the nn
model=Sequential()
model.add(Dense(input_dim=2,units=1))

# compile the model
model.compile(optimizer='sgd',loss='mse')

# train
print('training-----------------------------------')
for step in range(5000):
    cost=model.train_on_batch(X_train,Y_train)
    print('cost:',cost)

print('testing------------------------------------')
cost=model.evaluate(X_test,Y_test,batch_size=400)
print('test cost:',cost)
W,b=model.layers[0].get_weights()
print("X1的系数:",W[0])
print('X2的系数:',W[1])
print('截距:',b)
