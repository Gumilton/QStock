import sys, argparse

def splitInputArgComma(arg):
    return arg.split(",")

def argParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--train", action = "store_true", dest = "train", default=False)
    parser.add_argument("-v", "--verbose", action = "store_true", dest = "verbose", default=False)
    parser.add_argument("-d", "--today", dest = "today", type=str, required = False)
    parser.add_argument("-b", "--begin", dest = "startTrainDate", type=str, required = False)
    parser.add_argument("-e", "--end", dest = "endTrainDate", type=str, required = False)
    parser.add_argument("-s", "--stock", dest = "stocks", type=splitInputArgComma, required = True)


    args = parser.parse_args()


    print(args)

    if args.train:
        if args.startTrainDate == None or args.endTrainDate == None:
            parser.error('must specify start date or end date for training model')


if __name__ == "__main__":
    argParser()