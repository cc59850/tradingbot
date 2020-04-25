import os
import json
import time
import math
import keras
import matplotlib.pyplot as plt
from packages import data as DATA
from packages.model import Model
import pandas as pd
import numpy as np

TARGET = "High"
JSONFILE='trades.json'

def plot_results(predicted_data, true_data):
    fig = plt.figure(facecolor='white', figsize=(64, 36))
    ax = fig.add_subplot(111)
    ax.plot(true_data, label='True Data', linewidth=0.5)
    plt.plot(predicted_data, label='Prediction', linewidth=0.5)
    plt.legend()
    plt.savefig(str(TARGET) + ".jpg")
    plt.show()


def plot_results_multiple(predicted_data, true_data, prediction_len):
    fig = plt.figure(facecolor='white')
    ax = fig.add_subplot(111)
    ax.plot(true_data, label='True Data')
    # Pad the list of predictions to shift it in the graph to it's correct start
    for i, data in enumerate(predicted_data):
        padding = [None for p in range(i * prediction_len)]
        plt.plot(padding + data, label='Prediction')
        plt.legend()
    plt.show()


def main(model=None, target=None, file=None):
    if model:
        configs = json.load(open('../configs/'+JSONFILE, 'r'))
        data = DATA.Data(
            os.path.join('../data', configs['data']['filename']),
            configs['data']['train_test_split'],
            configs['data']['columns'],
            configs['data']['normalise']
        )
    else:
        configs = json.load(open('../configs/'+JSONFILE, 'r'))
        if not os.path.exists(configs['model']['save_dir']): os.makedirs(configs['model']['save_dir'])
        data = DATA.Data(
            os.path.join('../data', configs['data']['filename']),
            configs['data']['train_test_split'],
            configs['data']['columns'],
            configs['data']['normalise']
        )
        model = Model()
        model.build_model(configs)

    x, y = data.get_train_data()
    # 将目标值改为one hot 形态
    # y = data.restore(y, configs['data']['normalise'])
    # y = keras.utils.to_categorical(y, 40)
    # in-memory training
    model.train(
        x,
        y,
        epochs=configs['training']['epochs'],
        batch_size=configs['training']['batch_size'],
        save_dir=configs['model']['save_dir']
    )

    # out-of memory generative training
    # steps_per_epoch = math.ceil((data.len_train - 1000) / configs['training']['batch_size'])
    # model.train_generator(
    #     data_gen=data.generate_train_batch(
    #         batch_size=configs['training']['batch_size'],
    #         target_col=target
    #     ),
    #     epochs=configs['training']['epochs'],
    #     batch_size=configs['training']['batch_size'],
    #     steps_per_epoch=steps_per_epoch,
    #     save_dir=configs['model']['save_dir']
    # )
    #
    x_test, y_test = data.get_test_data()
    # y_test = data.restore(y_test, configs['data']['normalise'])
    # y_test = keras.utils.to_categorical(y_test, 40)
    # predictions = model.predict_sequences_multiple(x_test, configs['data']['sequence_length'], configs['data']['sequence_length'])
    # predictions = model.predict_sequence_full(x_test, configs['data']['sequence_length'])
    predictions = model.predict_point_by_point(x_test)

    configs = json.load(open('../configs/'+JSONFILE, 'r'))
    filename = os.path.join('../data', configs['data']['statistical_filename'])

    # 恢复数据
    predictions = data.restore(predictions, method=configs['data']['normalise'])
    y_test = data.restore(y_test, method=configs['data']['normalise'])
    y_test = np.reshape(y_test, (y_test.size,))

    # plot_results_multiple(predictions, y_test, configs['data']['sequence_length'])
    plot_results(predictions, y_test)

    # 获取时间，并封装
    configs = json.load(open('../configs/'+JSONFILE, 'r'))
    filename = os.path.join('../data', configs['data']['filename'])
    # dates=data.get_dates(filename,y_test.shape[0])
    return (predictions, y_test)
    # 添加时间序列


def xxx():
    predictions = []
    y_tests = []
    for target in [-1]:
        # model=Model()
        # model.load_model('./saved_models/24042020-210825-e100.h5')
        prediction, y_test = main(model=None, target=target)
        predictions.append(prediction)
        y_tests.append(y_test)

    df = pd.DataFrame(data={
        "predict_price": np.around(list(predictions[0].reshape(-1)), decimals=4),
        "real_price": np.around(list(y_tests[0].reshape(-1)), decimals=4),
    })
    df.to_csv("result" + ".csv", sep=',', index=None)


def learn_from_many_stocks():
    model = Model()
    configs = json.load(open('equal30.json', 'r'))
    model.build_model(configs)
    for t in [10]:
        for file in os.listdir('data/normalized/'):
            main(model, target=t, file=file)


if __name__ == '__main__':
    xxx()

    # 多样本学习
    # learn_from_many_stocks()
