import numpy as np
import pandas as pd
import pickle
import random

def get_data_from_excel(excepath, sheetname):
    #obtain data and label from excel files
    data = pd.read_excel(excepath, sheet_name=sheetname, header=0)
    names = [name for name in data]
    data_all = []
    label_all = []
    for i in range(len(names)-1):
        values = [value[i+1] for value in data.values]
        label_all.append(names[i+1])
        data_all.append(values)
    return data_all, label_all


def get_all_datas_from_excel():
    # save data in temper_data, temper_label, GLU_data, GLU_label, DO_data, DO_label
    excel_path = "smooth.xlsx"
    temper_data, temper_label = get_data_from_excel(excel_path, "temp")
    GLU_data, GLU_label = get_data_from_excel(excel_path, "calcium")
    DO_data, DO_label = get_data_from_excel(excel_path, "sodium")
    Na_data, Na_label = get_data_from_excel(excel_path, "pH")
    return temper_data, temper_label, GLU_data, GLU_label, DO_data, DO_label,Na_data, Na_label


def ava_filter(x, window):
    # define average filter
    N = len(x)
    res = []
    for i in range(N):
        if i <= window // 2 or i >= N - (window // 2):
            temp = x[i]
        else:
            sum = 0
            for j in range(window):
                sum += x[i - window // 2 + j]
            temp = sum * 1.0 / window
        res.append(temp)
    return res


def noise_reduction(temper_data):
    # noise reduction
    for i in range(len(temper_data)):
        x = temper_data[i]
        for j in range(5):
            res = ava_filter(x, window=4)
        temper_data[i] = res
    return temper_data


def data_normal(datas):
    #min-max normalization
    data_max = max(max(datas))
    data_min = min(min(datas))
    for i in range(len(datas)):
        for j in range(len(datas[i])):
            datas[i][j] = (datas[i][j] - data_min) / (data_max - data_min)
    return datas


def add_data_405(temper_data, temper_label, GLU_data, GLU_label, PH_data, PH_label):
    # generate merge spectrum by add three types of data
    N1 = len(temper_data)
    N2 = len(GLU_data)
    N3 = len(PH_data)
    datas = {}
    for i in range(N1):
        for j in range(N2):
            for k in range(N3):
                temper_array_i = np.array(temper_data[i])
                GLU_data_j = np.array(GLU_data[j])
                PH_data_k = np.array(PH_data[k])
                data = temper_array_i + GLU_data_j + PH_data_k
                label = (temper_label[i], GLU_label[j], PH_label[k])
                datas[label] = data
                #print(label)
    return datas

def add_data_450(temper_data, temper_label, Na_data, Na_label, Ca_data, Ca_label):
    # generate merge spectrum by add three types of data
    N1 = len(temper_data)
    N2 = len(Na_data)
    N3 = len(Ca_data)
    datas = {}
    for i in range(N1):
        for j in range(N2):
            for k in range(N3):
                temper_array_i = np.array(temper_data[i])
                Na_data_j = np.array(Na_data[j])
                Ca_data_k = np.array(Ca_data[k])
                data = temper_array_i + Na_data_j + Ca_data_k
                label = (temper_label[i], Na_label[j], Ca_label[k])
                datas[label] = data
                #print(label)
    return datas

def data_preprocess():
    # main of data preprocess
    output_path="multi780.xlsx"
    writer = pd.ExcelWriter(output_path)
    temper_data, temper_label, GLU_data, GLU_label, DO_data, DO_label, Na_data, Na_label = get_all_datas_from_excel()
     # temper_data = noise_reduction(temper_data)
     # temper_data = data_normal(temper_data)
     # Na_data = data_normal(Na_data)
     # temper_data = data_normal(temper_data)
     # GLU_data = data_normal(GLU_data)
    #  DO_data = data_normal(DO_data)
    data405= add_data_405(temper_data, temper_label, GLU_data, GLU_label, DO_data, DO_label)
    #data450 = add_data_450(temper_data, temper_label, Na_data, Na_label)
    df405 = pd.DataFrame.from_dict(data405)
    #df450 = pd.DataFrame.from_dict(data450)
    df405.to_excel(writer, sheet_name='combo405')
    #df450.to_excel(writer, sheet_name='combo450')
    writer.save()
    writer.close()

def datasplit():
    # train test validation split, 5-fold cross validation, save data in pkl files
    with open(r"all_datas.pkl", "rb") as f:
        load_datas = pickle.load(f)
    labels = list(load_datas.keys())
    random.shuffle(labels)
    train_label1 = labels[0:400]
    valid_label1 = labels[400:500]
    train_label2 = labels[0:300] + labels[400:500]
    valid_label2 = labels[300:400]
    train_label3 = labels[0:200] + labels[300:500]
    valid_label3 = labels[200:300]
    train_label4 = labels[0:100] + labels[200:500]
    valid_label4 = labels[100:200]
    train_label5 = labels[100:500]
    valid_label5 = labels[0:100]
    test_label = labels[500:]
    with open(r"train1.pkl", 'wb') as f:
        pickle.dump(train_label1, f)
    with open(r"valid1.pkl", 'wb') as f:
        pickle.dump(valid_label1, f)
    with open(r"train2.pkl", 'wb') as f:
        pickle.dump(train_label2, f)
    with open(r"valid2.pkl", 'wb') as f:
        pickle.dump(valid_label2, f)
    with open(r"train3.pkl", 'wb') as f:
        pickle.dump(train_label3, f)
    with open(r"valid3.pkl", 'wb') as f:
        pickle.dump(valid_label3, f)
    with open(r"train4.pkl", 'wb') as f:
        pickle.dump(train_label4, f)
    with open(r"valid4.pkl", 'wb') as f:
        pickle.dump(valid_label4, f)
    with open(r"train5.pkl", 'wb') as f:
        pickle.dump(train_label5, f)
    with open(r"valid5.pkl", 'wb') as f:
        pickle.dump(valid_label5, f)
    with open(r"test.pkl", 'wb') as f:
        pickle.dump(test_label, f)


if __name__ == '__main__':
    data_preprocess()
    #datasplit()
