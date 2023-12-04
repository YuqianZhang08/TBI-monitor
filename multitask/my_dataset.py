import torch
from torch.utils.data import Dataset
import os
import pickle


class myDataSet(Dataset):
    #generate dataset
    def __init__(self, data_root, transforms=None, model_name: str = "train"):
        self.data_root = data_root
        self.model_name = model_name

        data_path = os.path.join(data_root, r"all_data.pkl")
        assert os.path.exists(data_path), "not found {} file.".format(data_path)
        if model_name == 'train':
            train_label_path = os.path.join(data_root, r"train.pkl")
            assert os.path.exists(train_label_path), "not found {} file.".format(train_label_path)
            self.my_label = pickle.load(open(train_label_path, 'rb'))
        elif model_name == 'valid':
            valid_label_path = os.path.join(data_root, r"valid.pkl")
            assert os.path.exists(valid_label_path), "not found {} file.".format(valid_label_path)
            self.my_label = pickle.load(open(valid_label_path, 'rb'))
        elif model_name == 'test':
            test_label_path = os.path.join(data_root, r"test.pkl")
            assert os.path.exists(test_label_path), "not found {} file.".format(test_label_path)
            self.my_label = pickle.load(open(test_label_path, 'rb'))

        all_data = pickle.load(open(data_path, 'rb'))
        self.my_data = [all_data[label] for label in self.my_label]
        self.transforms = transforms

    def __len__(self):
        return len(self.my_label)

    def __getitem__(self, idx):
        # convert everything into a torch.Tensor
        #data = torch.as_tensor(self.my_data[idx], dtype=torch.float32).unsqueeze(0)
        #label = torch.as_tensor(self.my_label[idx], dtype=torch.float32).unsqueeze(0)
        data = torch.as_tensor(self.my_data[idx], dtype=torch.float32)
        label = torch.as_tensor(self.my_label[idx], dtype=torch.float32)
        return data, label


if __name__ == '__main__':
    train_dataset = myDataSet('.\\stacked', model_name='test')

    train_data_loader = torch.utils.data.DataLoader(train_dataset,
                                                    batch_size=2,
                                                    shuffle=True)
    for n, (data, label) in enumerate(train_data_loader):
        print(n, data.shape, label.shape)
        print(label[0])
