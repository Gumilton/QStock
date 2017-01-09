import pickle
import pandas as pd
import util as ut
import numpy as np
from indicators import transform, getTokens


class Predictor():
    def __init__(self, args):
        self.actionMap = {0: np.NaN, 1:"BUY", 2:"SELL"}

    def loadModel(self, infile):
        with open(infile, 'rb') as input:
            self.learner = pickle.load(input)

    def query(self, symbol, sd, ed):
        dates = pd.date_range(sd, ed)
        prices_all = ut.readStocks(symbol, dates)  # automatically adds SPY
        prices = prices_all[symbol]  # only portfolio symbols
        trades_SPY = prices_all['SPY']  # only SPY, for comparison later

        indi = transform(prices[symbol])
        tokens = getTokens(indi)

        # print(tokens)
        # print(symbol)

        orders = pd.DataFrame(index=tokens.index, columns=["Symbol", "Order", "Shares"])

        # print(orders)
        orders.ix[:, "Symbol"] = symbol[0]
        orders.ix[:, "Shares"] = 10.0

        dateInd = 0

        while dateInd < tokens.shape[0]:
            action = self.learner.querysetstate(int(tokens.iloc[dateInd, 0]))
            orders.iloc[dateInd, 1] = self.actionMap[action]
            dateInd += 1

        orders.dropna(inplace=True)
        cleaned = ut.cleanOrders(orders)

        return cleaned
