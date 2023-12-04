import torch.nn as nn
import torch


class Multi_CNN(nn.Module):
    # define CNN model which consist of 2 2D conv and 1 1D conv
    def __init__(self, num_inputs=3, num_outputs=6, num_hiddens=12, device=torch.device('cpu')):
        super().__init__()
        self.device = device
        self.num_input = num_inputs
        self.net = nn.Sequential(
            #nn.BatchNorm2d(self.num_input),
            nn.Conv2d(num_inputs, num_hiddens, kernel_size=3, stride=1, padding=1, dilation=2),
            #nn.MaxPool2d(2),
            nn.ReLU(),
            #nn.BatchNorm2d(num_hiddens*4),
            nn.Conv2d(num_hiddens, num_hiddens*2, kernel_size=3, stride=1),
            #nn.MaxPool2d(2),
            nn.ReLU(),
            #nn.BatchNorm2d(num_hiddens),
            nn.Conv2d(num_hiddens*2, num_outputs, 3, 1),
            nn.MaxPool2d(2),
            nn.ReLU(),
            )
        self.conv1 = nn.Sequential(
            #nn.BatchNorm1d(400),
            nn.Conv1d(720, 6, 1, 1),
        )
        self.lin1 = nn.Sequential(
            #nn.BatchNorm1d(720),
            #nn.Linear(2940,720),   #for the one without maxpool
            nn.Linear(552,36),  #720
            nn.Linear(36,6),
        )
        


    def forward(self, inputs):
        inputs = inputs.view(-1, 3,14,53)
        #zeros = torch.zeros(inputs.shape[0], 45, 1).to(self.device)
        #inputs = torch.cat([inputs, zeros], dim=1)
        #inputs = inputs.view(-1, 1, 26, 26)
        out = self.net(inputs)
        out=torch.flatten(out,1)
        #out = out.view(-1, 400, 1)
        #out = torch.sigmoid(self.lin1(out))
        out=self.lin1(out)
        #out = out.view(-1, 1, 6)
        return out


class Multi_FNN(nn.Module):
     #define FNN which consist of 2 hidden layers and 1 output layer
    def __init__(self, num_inputs=631, num_outputs=6, num_hiddens=50):
        super().__init__()
        self.num_input = num_inputs
        self.net = nn.Sequential(
            nn.BatchNorm1d(self.num_input),
            nn.Linear(num_inputs, num_hiddens*4),
            nn.ReLU(),
            nn.BatchNorm1d(num_hiddens*4),
            nn.Linear(num_hiddens*4, num_hiddens),
            nn.ReLU(),
            nn.BatchNorm1d(num_hiddens),
            nn.Linear(num_hiddens, num_outputs),
            )

    def forward(self, inputs):
        inputs = inputs.view(-1, 631)
        out = self.net(inputs)
        out = out.view(-1, 1, 3)
        return out


if __name__ == '__main__':
    x = torch.randn((2, 1, 3, 14, 53))
    print(x.shape)
    net = Multi_CNN()
    out = net(x)
    print(out.shape)