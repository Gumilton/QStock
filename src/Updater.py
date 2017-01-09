import util as ut

loyal3Stocks = []

class Updater():
    def __init__(self, args):
        self.loyal3Stocks = ["M","KSS","AEO","BBY","GPS","TGT","HOME","INTC","AAPL","AXP","FOXA","NOK","PVH","DIS","DISCA", \
                             "MAT","TWX","VFC","HAS","SC","AMC","ATVI","DPS","LB","RL","WMT","GOOG","KATE","MCD","MDLZ", \
                             "MSFT","NKE","STOR","UL","BWLD","EA","VIA","YUM","ANF","BUD","DNKN","FTR","GLOB","HSY","KO",\
                             "PLAY","QSR","TWTR","YUMC","FB","FDC","GPRO","K","KHC","PEP","SBUX","WWE","MNST","BUFF",\
                             "YHOO","BABA","TDOC","BRK.B","GDDY","EIGI","VA","AMZN","NFLX","HUBS","SQ","TRUP"]
        self.args = args


    def update(self):
        for sym in self.args.stocks:
            try:
                ut.getWebStock(stockSym = sym, verbose = self.args.verbose)
            except Exception as inst:
                print(sym + " errors:")
                print(type(inst))
                print(inst.args)
                print(inst)