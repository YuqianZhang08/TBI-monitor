import torch
import utils
import torch.nn


def criterion(inputs, target):
    # define criterion
    loss = torch.nn.MSELoss(reduction='mean')
    losses = {}
    averagedloss={}
    losses['out'] = loss(inputs, target)
    losspH = loss(inputs[:,0], target[:,0])
    lossGlu = loss(inputs[:,1], target[:,1])
    lossDo = loss(inputs[:,2], target[:,2])
    lossT = loss(inputs[:,3], target[:,3])
    lossNa = loss(inputs[:,4], target[:,4])
    lossCa = loss(inputs[:,5], target[:,5])
    averagedloss['out']=0.055*losspH+0.05*lossDo+lossCa+0.1*lossGlu+0.001*lossNa+0.012*lossT    #0.003
    
    return averagedloss['out']


def evaluate(model, data_loader, device):
    # evaluation '
    model.eval()
    metric_logger = utils.MetricLogger(delimiter="  ")
    metric_logger.add_meter('loss', utils.SmoothedValue(window_size=1, fmt='{value:.6f}'))
    header = 'Test:'
    with torch.no_grad():
        for image, target in metric_logger.log_every(data_loader, 1, header):
            image, target = image.to(device), target.to(device)
            output = model(image)
            loss = criterion(output, target)
            metric_logger.update(loss=loss)

    return metric_logger.meters["loss"].global_avg


def train_one_epoch(model, optimizer, data_loader, device, epoch, lr_scheduler, print_freq=1):
    #  processes of each epoch
    model.train()
    metric_logger = utils.MetricLogger(delimiter="  ")
    metric_logger.add_meter('lr', utils.SmoothedValue(window_size=1, fmt='{value:.6f}'))
    header = 'Epoch: [{}]'.format(epoch)

    for image, target in metric_logger.log_every(data_loader, print_freq, header):
        image, target = image.to(device), target.to(device)
        output = model(image)
        loss = criterion(output, target)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        lr_scheduler.step()

        lr = optimizer.param_groups[0]["lr"]
        if lr <= 0.000001:
            lr = 0.000001
        metric_logger.update(loss=loss.item(), lr=lr)

    return metric_logger.meters["loss"].global_avg, lr


def create_lr_scheduler(optimizer,
                        num_step: int,
                        epochs: int,
                        warmup=True,
                        warmup_epochs=1,
                        warmup_factor=1e-3):
    assert num_step > 0 and epochs > 0

    def f(x):

        if warmup is True and x <= (warmup_epochs * num_step):
            alpha = float(x) / (warmup_epochs * num_step)

            return warmup_factor * (1 - alpha) + alpha
        else:

            return (1 - (x - warmup_epochs * num_step) / ((epochs - warmup_epochs) * num_step)) ** 0.9

    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=f)
