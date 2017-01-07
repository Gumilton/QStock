import argparse
from Trainer import Trainer
from Predictor import Predictor
from Updater import Updater

def splitInputArgComma(arg):
    return arg.split(",")

def argParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ["train", "predict", "update"], dest = "mode", required = True)
    parser.add_argument("-s", "--stock", dest = "stocks", type=splitInputArgComma, required = False)
    parser.add_argument("-d", "--today", dest = "today", type=str, required = False)
    parser.add_argument("-b", "--begin", dest = "startTrainDate", type=str, required = False)
    parser.add_argument("-e", "--end", dest = "endTrainDate", type=str, required = False)
    parser.add_argument("-a", "--all", dest = "allStocks", action ="store_true", required = False, default=False)
    parser.add_argument("-v", "--verbose", action = "store_true", dest = "verbose", default=False)
    parser.add_argument("--num_states", dest = "num_states", default=100)
    parser.add_argument("-w", "--window", dest = "window", default=10)
    parser.add_argument("--num_actions", dest = "num_actions", default = 4)
    parser.add_argument("--alpha", dest = "alpha", default = 0.2)
    parser.add_argument("--gamma", dest = "gamma", default = 0.9)
    parser.add_argument("--rar", dest = "rar", default = 0.5)
    parser.add_argument("--radr", dest = "radr", default = 0.99)
    parser.add_argument("--dyna", dest = "dyna", default = 0)


    args = parser.parse_args()
    print(args)

    if args.stocks == None and not args.allStocks:
        parser.error('must specify stocks used for training, by -s [--stock] or -a [--all] for all available stocks')

    #//TODO: process stock symbols

    if args.mode == "train":
        if args.startTrainDate == None or args.endTrainDate == None:
            parser.error('must specify start date or end date for training model')
        # //TODO: check date correctness
    elif args.mode == "predict":
        if args.today == None:
            parser.error('must specify date to suggest action')
        # //TODO: check date correctness
    else:
        pass

    return args

def handler(args):
    if args.mode == "train":
        trainer = Trainer(args)
    elif args.mode == "predict":
        predicter = Predictor(args)
    else:
        updater = Updater(args)

if __name__ == "__main__":
    args = argParser()
    handler(args)