import os
import time

import matplotlib.gridspec as gridspec
import torch
from matplotlib import pyplot as plt

from multitask.models import Multi_CNN, Multi_FNN
from multitask.my_dataset import myDataSet


def create_model(net_name, device):
    #create model
    if net_name == "CNN":
        net = Multi_CNN(num_inputs=3, num_outputs=6, device=device)
    elif net_name == "FNN":
        net = Multi_FNN(num_inputs=3*14*53, num_outputs=6)
    return net


def time_synchronized():
    # time calculation
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    return time.time()

def predictdata(device, image, net_name):

    # create model
    model = create_model(net_name, device)

    # load train weights
    train_weights = f"weight-model_{net_name}.pth"
    assert os.path.exists(train_weights), "{} file dose not exist.".format(train_weights)
    model.load_state_dict(torch.load(train_weights, map_location=device)["model"])
    model.to(device)
    model.eval()  # evaluation mode
    with torch.no_grad():
        prediction_sign = model(image.to(device))  # prediction
            #print(int(n), prediction_sign, target)
    return prediction_sign
    
    
def main(data_path, model_name, net_name):
    device = "cpu"
    print("using {} device.".format(device))
    # load validation data set
    val_dataset = myDataSet(data_path, model_name=model_name)
    val_data_set_loader = torch.utils.data.DataLoader(val_dataset,
                                                      batch_size=1,
                                                      shuffle=False)
    predictions = []
    targets = []
    for n, (image, target) in enumerate(val_data_set_loader):
        image, target = image.to(device), target.to(device)
        prediction_sign=predictdata(device,image,net_name)
        predictions.append(prediction_sign[0])    
        targets.append(target[0])

    # R2 calculation
    Arrprediction=torch.stack(predictions)
    Arrtargets=torch.stack(targets)
    sub=Arrprediction-Arrtargets
    RSS=torch.sum(torch.mul(sub, sub),dim=0)
    targetmean=torch.mean(Arrtargets,axis=0)
    TSS=torch.sum(torch.mul((Arrtargets-targetmean),(Arrtargets-targetmean)),dim=0)
    R2=1-RSS/TSS
    MSE=RSS/len(sub)
    MAE=torch.sum(torch.abs(sub),dim=0)/len(sub)
    print("R2_pH:", float(R2[0]), "MSE_pH:", float(MSE[0]), "MAE_pH:", float(MAE[0]),'\n'
          "R2_DO:", float(R2[2]),"MSE_DO:", float(MSE[2]), "MAE_DO:", float(MAE[2]),'\n'
          "R2_Temperature:", float(R2[3]),"MSE_Temperature:", float(MSE[3]), "MAE_Temperature:", float(MAE[3]),'\n'
          "R2_Na:", float(R2[4]),"MSE_Na:", float(MSE[4]),"MAE_Na:", float(MAE[4]), '\n'
          "R2_Ca:", float(R2[5]),"MSE_Ca:", float(MSE[5]), "MAE_Ca:", float(MAE[5]),'\n'
          "R2_glucose:", float(R2[1]),"MSE_glucose:",float(MSE[1]), "MAE_glucose:", float(MAE[1]))

    gs = gridspec.GridSpec(3, 1)
    gs.update(wspace=0.8, hspace=0.6)
    plt.subplot(gs[0, 0])
    plt.ylabel("Prediction Value", fontsize=10)
    plt.title("Temperature", fontsize=10, fontweight='bold')
    x = [range(len(predictions))]
    p = [float(v[0]) for v in predictions]
    t = [float(v[0]) for v in targets]
    typ1 = plt.scatter(x, p, color='blue', marker='+')
    typ2 = plt.scatter(x, t, color='red', marker='x')
    plt.legend((typ1, typ2), ('predict value', 'ground truth'))

    plt.subplot(gs[1, 0])
    plt.ylabel("Prediction Value", fontsize=10)
    plt.title("GLU", fontsize=10, fontweight='bold')
    x = [range(len(predictions))]
    p = [float(v[1]) for v in predictions]
    t = [float(v[1]) for v in targets]
    plt.scatter(x, p, color='blue', marker='+')
    plt.scatter(x, t, color='red', marker='x')

    plt.subplot(gs[2, 0])
    plt.xlabel("Test data's id", fontsize=10)
    plt.ylabel("Prediction Value", fontsize=10)
    plt.title("PH", fontsize=10, fontweight='bold')
    x = [range(len(predictions))]
    p = [float(v[2]) for v in predictions]
    t = [float(v[2]) for v in targets]
    plt.scatter(x, p, color='blue', marker='+')
    plt.scatter(x, t, color='red', marker='x')

    plt.show()


if __name__ == '__main__':
    main(".", model_name="test", net_name="CNN")
