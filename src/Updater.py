import util as ut

loyal3Stocks = []

class Updater():
    def __init__(self, args):
        self.loyal3Stocks = ut.getLoyal3List()
        self.args = args


    def update(self):
        for sym in self.args.stocks:
            print("Updating " + sym)
            try:
                ut.getWebStock(stockSym = sym, verbose = self.args.verbose)
            except Exception as inst:
                print(sym + " errors:")
                print(type(inst))
                print(inst.args)
                print(inst)