import argparse
from Trainer import Trainer
from Predictor import Predictor
from Updater import Updater
import util as ut

def splitInputArgComma(arg):
    return arg.split(",")

def args2Stocks(arg):
    loyal3Stocks = ut.getLoyal3List()
    if arg.allStocks:
        return loyal3Stocks
    if arg.verbose:
        print("Input stocks: " + str(arg.stocks))
    tempStocks = arg.stocks
    stock = []
    for sym in tempStocks:
        if sym in loyal3Stocks:
            stock.append(sym)
        else:
            print("".join(["Input stock ", sym, " is not available for trading"]))
    return stock

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


    args.stocks = args2Stocks(args)


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
        updater.update()

if __name__ == "__main__":
    args = argParser()
    handler(args)