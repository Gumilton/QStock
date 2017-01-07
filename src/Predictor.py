import pickle
import pandas as pd
import util as ut
import numpy as np

class Predictor():
    def __init__(self, args):
        self.actionMap = {0: np.NaN, 1:"BUY", 2:"SELL"}

    def loadModel(self, infile):
        with open(infile, 'rb') as input:
            self.learner = pickle.load(input)

    def query(self, symbol, sd, ed):
        dates = pd.date_range(sd, ed)
        prices_all = ut.readStock(symbol, dates)  # automatically adds SPY
        prices = prices_all[symbol]  # only portfolio symbols
        trades_SPY = prices_all['SPY']  # only SPY, for comparison later

        indi = self.transform(prices[symbol])
        tokens = self.getTokens(indi)

        orders = pd.DataFrame(index=tokens.index, columns=["Symbol", "Order", "Shares"])
        orders["Symbol"] = symbol
        orders["Shares"] = 1000.0

        dateInd = 0

        while dateInd < tokens.shape[0]:
            action = self.learner.querysetstate(int(tokens.iloc[dateInd,0]))
            orders.iloc[dateInd,1] = self.actionMap[action]
            dateInd += 1

        orders.dropna(inplace=True)
        indices = [0]
        orders.iloc[0,2] = 500
        status = orders.iloc[0,1]
        for i in range(1, orders.shape[0]):
            newStatus = orders.iloc[i,1]
            if newStatus != status:
                indices.append(i)
                status = newStatus

        cleanOrders = orders.iloc[indices,:]
        trades = pd.DataFrame(0, index=prices.index, columns=[symbol])
        trades.ix[(cleanOrders[cleanOrders.iloc[:,1] == "SELL"]).index] = -1000
        trades.ix[(cleanOrders[cleanOrders.iloc[:,1] == "BUY"]).index] = 1000
        firstIndex = trades[trades.iloc[:,0] != 0].index[0]
        trades.ix[firstIndex] = trades.ix[firstIndex] / abs(trades.ix[firstIndex]) * 500

        # trades.values[:,:] = 0 # set them all to nothing
        # trades.values[3,:] = 500 # add a BUY at the 4th date
        # trades.values[5,:] = -500 # add a SELL at the 6th date
        # trades.values[6,:] = -500 # add a SELL at the 7th date
        # trades.values[8,:] = 1000 # add a BUY at the 9th date
        # if self.verbose: print type(trades) # it better be a DataFrame!
        # if self.verbose: print trades
        # if self.verbose: print prices_all
        return trades
