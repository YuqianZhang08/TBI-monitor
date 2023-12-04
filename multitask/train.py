import torch

import argparse
import datetime
import os
import sys

from models import Multi_CNN, Multi_FNN
import train_eval_utils
from my_dataset import myDataSet
from plot_curve import plot_loss_and_lr, plot_map
from utils import Logger


def create_model(device):
    #create model
    if args.net_name == "CNN":
        net = Multi_CNN(num_inputs=3, num_outputs=6, device=device)
    elif args.net_name == "FNN":
        net = Multi_FNN(num_inputs=3*14*53, num_outputs=6)
    else:
        net = None
    return net


def main(args):
    torch.manual_seed(0)

    # set device
    if not args.disable_cuda and torch.cuda.is_available():
        device = torch.device('cuda')
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    else:
        device = torch.device('cpu')
    print("Using {} device training.".format(device.type))
    sys.stdout.flush()

    # save result
    results_file = "results{}.txt".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))

    # set preprocess
    data_path = args.data_path
    if os.path.exists(data_path) is False:
        raise FileNotFoundError("data dose not in path:'{}'.".format(data_path))

    # load train data set
    train_dataset = myDataSet(data_path, transforms=None, model_name="train")

    train_data_loader = torch.utils.data.DataLoader(train_dataset,
                                                    batch_size=args.batch_size,
                                                    shuffle=True)

    # load validation data set
    val_dataset = myDataSet(data_path, transforms=None, model_name="valid")
    val_data_set_loader = torch.utils.data.DataLoader(val_dataset,
                                                      batch_size=args.val_batch_size,
                                                      shuffle=False)

    # define model
    model = create_model(device)
    model.to(device)
    # print(model)

    # define optimizer
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.RMSprop(
        params,
        lr=args.learning_rate,
        alpha=0.99
    )

    # learning rate scheduler
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer,
                                                   step_size=args.step_size,
                                                   gamma=0.5)


    if args.resume != '':
        checkpoint = torch.load(args.resume, map_location='cpu')
        model.load_state_dict(checkpoint['model'])
        optimizer.load_state_dict(checkpoint['optimizer'])
        lr_scheduler.load_state_dict(checkpoint['lr_scheduler'])
        args.start_epoch = checkpoint['epoch'] + 1
        print("the training process from epoch{}...".format(args.start_epoch))
        sys.stdout.flush()

    train_loss = []
    learning_rate = []
    val_map = []
    mean_loss_re = 9999

    for epoch in range(args.start_epoch, args.epochs):
        mean_loss, lr = train_eval_utils.train_one_epoch(model, optimizer, train_data_loader, device,
                                                         epoch, lr_scheduler=lr_scheduler, print_freq=args.print_freq)

        val_loss = train_eval_utils.evaluate(model, val_data_set_loader, device=device)
        val_info = f"val_loss: {val_loss}"

        train_loss.append(mean_loss)
        learning_rate.append(lr)

        # update the learning rate
        lr_scheduler.step()

        # write into txt
        with open(results_file, "a") as f:
            #  record train_loss and lr for each epoch
            train_info = f"[epoch: {epoch}]\n" \
                         f"train_loss: {mean_loss:.4f}\n" \
                         f"lr: {lr:.6f}\n"
            f.write(train_info + val_info + "\n\n")

        # save weights
        save_files = {
            'model': model.state_dict(),
            'optimizer': optimizer.state_dict(),
            'lr_scheduler': lr_scheduler.state_dict(),
            'epoch': epoch,
            'args': args}

        # save for each 10 epoch
        if mean_loss < mean_loss_re:
            torch.save(save_files, f"./{args.output_dir}/weight-model_{args.net_name}.pth")
            mean_loss_re = mean_loss
            print("save new model...")

    # plot loss and lr curve
    if len(train_loss) != 0 and len(learning_rate) != 0:
        plot_loss_and_lr(train_loss, learning_rate)

    # plot mAP curve
    if len(val_map) != 0:
        plot_map(val_map)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pytorch training')

    parser.add_argument('--disable_cuda',   default=False,   action='store_true', help='Disable CUDA')
    parser.add_argument('--data_path',      default=r'.\\stacked',    type=str, help='Data address')
    parser.add_argument('--output_dir',     default='.', type=str, help='path where to save')
    parser.add_argument('--net_name',   default="CNN",       type=str, help='Model name')
    parser.add_argument('--batch_size',     default=5,       type=int, help='Train batch size')
    parser.add_argument('--val_batch_size', default=5,       type=int, help='Validation batch size')
    parser.add_argument('--epochs',         default=5,     type=int, metavar='N', help='number of total epochs to run')
    parser.add_argument('--learning_rate',  default=0.001,    type=float, help='Learning rate')
    parser.add_argument('--step_size',      default=1500, type=int, help='Learning rate decay step size')
    parser.add_argument('--print_freq',     default=5,       type=int, help='log print freq')

    parser.add_argument('--resume',         default='')
    parser.add_argument('--start_epoch',    default=0,       type=int, help='Start epoch')  

    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    sys.stdout = Logger(r"print_log0.1.txt")
    sys.stdout.flush()

    main(args)

