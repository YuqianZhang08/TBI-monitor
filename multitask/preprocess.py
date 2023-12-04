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


def get_all_data_from_excel(excel_path):
    # save data in temper_data, temper_label, GLU_data, GLU_label, DO_data, DO_label
    
    temper_data, temper_label = get_data_from_excel(excel_path, "Temperature")
    GLU_data, GLU_label = get_data_from_excel(excel_path, "Glucose")
    DO_data, DO_label = get_data_from_excel(excel_path, "O2")
    Na_data, Na_label = get_data_from_excel(excel_path, "Sodium")
    pH_data, pH_label = get_data_from_excel(excel_path, "pH")
    Ca_data, Ca_label = get_data_from_excel(excel_path, "Calcium")
    return temper_data, temper_label, GLU_data, GLU_label, DO_data, DO_label,Na_data, Na_label, pH_data, pH_label, Ca_data, Ca_label


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


def data_normal(data):
    #min-max normalization
    data_max = np.max(data)
    data_min = np.min(data)
    for i in range(len(data)):
        for j in range(len(data[i])):
            data[i][j] = (data[i][j] - data_min) / (data_max - data_min)
    return data


def add_data_405(pH_data, pH_label,  GLU_data, GLU_label, DO_data, DO_label):
    # generate merge spectrum by add three types of data
    N1 = len(pH_data)
    N2 = len(GLU_data)
    N3 = len(DO_data)
    dataall = {}
    for i in range(N1):
        for j in range(N2):
            for k in range(N3):
                pH_array_i = np.array(pH_data[i])
                GLU_data_j = np.array(GLU_data[j])
                DO_data_k = np.array(DO_data[k])
                data = pH_array_i + GLU_data_j + DO_data_k
                label = (pH_label[i], GLU_label[j], DO_label[k])
                dataall[label] = data
                #print(label)
    return dataall

def add_data_450(temper_data, temper_label, Na_data, Na_label):
    # generate merge spectrum by add three types of data
    N1 = len(temper_data)
    N2 = len(Na_data)
    dataall = {}
    for i in range(N1):
        for j in range(N2):
                temper_array_i = np.array(temper_data[i])
                Na_data_j = np.array(Na_data[j])
                data = temper_array_i + Na_data_j
                label = (temper_label[i], Na_label[j])
                dataall[label] = data
                #print(label)
    return dataall

def add_data_540(Ca_data, Ca_label):
    # generate merge spectrum by add three types of data
    N1 = len(Ca_data)
    dataall = {}
    for i in range(N1):
        data = np.array(Ca_data[i])
        label = (Ca_label[i],)
        dataall[label] = data
        #print(label)
    return dataall
def dataforML(data405, data450,data540,):
    N1 = len(data405)
    N2 = len(data450)
    N3 = len(data540)
    index405=list(data405.keys())
    index450=list(data450.keys())
    index540=list(data540.keys())
    specall={}
    for i in range (N1):
        for j in range (N2):
            for k in range (N3):
                data=np.hstack((data405[index405[i]][0:230],data405[index405[i]][533:],data450[index450[j]], data540[index540[k]][292:654]))
                label=index405[i]+index450[j]+index540[k]
                specall[label] = data
    return specall
def Com3Channel(data405, data450,data540, verticle=True,size=(14,53)):
    # generate merge spectrum by add three types of data
    # if verticle =Ture, stack three channels if = Flase, add the three channels into one channel
    N1 = len(data405)
    N2 = len(data450)
    N3 = len(data540)
    index405=list(data405.keys())
    index450=list(data450.keys())
    index540=list(data540.keys())
    dataall = {}
    for i in range(N1):
        for j in range(N2):
            for k in range(N3):
                if (verticle):
                    data=(np.array(data405[index405[i]]).reshape(size),np.array(data450[index450[j]]).reshape(size),np.array(data540[index540[k]]).reshape(size))
                else:
                    data=data405[index405[i]]+data450[index450[j]]+data540[index540[k]]
                label=index405[i]+index450[j]+index540[k]
                dataall[label] = data

                #b=np.array(data).flatten()
                #c=b.reshape(53,42)
                #plt.imshow(c)
                #plt.show()
                #plot.savefig('datavisualization\'+label+'.png')
        #print(label)
    return dataall

def data_preprocess(excel_path):
    # main of data preprocess
    output_path="multi3.xlsx"
    writer = pd.ExcelWriter(output_path)
    temper_data, temper_label, GLU_data, GLU_label, DO_data, DO_label, Na_data, Na_label, pH_data, pH_label, Ca_data, Ca_label = get_all_data_from_excel(excel_path)
     # temper_data = noise_reduction(temper_data)
    temper_data = data_normal(temper_data)
    Na_data = data_normal(Na_data)
    Ca_data = data_normal(Ca_data)
    GLU_data = data_normal(GLU_data)
    DO_data = data_normal(DO_data)
    pH_data=data_normal(pH_data)
    
    data405= add_data_405(pH_data, pH_label,  GLU_data, GLU_label, DO_data, DO_label)
    data450 = add_data_450(temper_data, temper_label, Na_data, Na_label)
    data540= add_data_540(Ca_data, Ca_label)

    '''
    df405 = pd.DataFrame.from_dict(data405)
    df450 = pd.DataFrame.from_dict(data450)
    df540 = pd.DataFrame.from_dict(data540)
    df405.to_excel(writer, sheet_name='combo405')
    df450.to_excel(writer, sheet_name='combo450')
    df540.to_excel(writer, sheet_name='combo540')
    writer.save()
    writer.close()
    '''
    #Stackdata=Com3Channel(data405, data450,data540)
    Stackdata=dataforML(data405, data450,data540)
    
    with open(r"ml_data.pkl", 'wb') as f:
        pickle.dump(Stackdata, f)
    
def datasplit():
    # train test validation split, 5-fold cross validation, save data in pkl files
    with open(r"all_data.pkl", "rb") as f:
        load_data = pickle.load(f)
    labels = list(load_data.keys())
    random.shuffle(labels)
    train_label=labels[0:14063]
    valid_label=labels[14063:18750]
    train_label1 = labels[0:2800]
    valid_label1 = labels[2800:3750]
    train_label2 = labels[3750:6550] 
    valid_label2 = labels[6550:7500]
    train_label3 = labels[10300:13100]
    valid_label3 = labels[13100:11250]
    train_label4 = labels[11250:14050]
    valid_label4 = labels[14050:15000]
    train_label5 = labels[15000:17800]
    valid_label5 = labels[17800:18750]
    test_label = labels[12500:14050]
    
    with open(r"train.pkl", 'wb') as f:
        pickle.dump(train_label, f)
    with open(r"valid.pkl", 'wb') as f:
        pickle.dump(valid_label, f)
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
    excel_path = "test.xlsx"   #18750 data
    data_preprocess(excel_path)
    print ("end")
    #datasplit()
