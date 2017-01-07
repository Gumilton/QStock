import numpy as np
import random as rand
import pandas as pd
import util as ut
import pickle


class QLearner(object):

    def __init__(self, args):

        self.verbose = args.verbose
        self.num_actions = args.num_actions
        self.s = 0
        self.a = 0
        self.q = np.random.rand(args.num_states, args.num_actions) * 2 - 1
        self.alpha = args.alpha
        self.gamma = args.gamma
        self.rar = args.rar
        self.radr = args.radr
        self.dyna = args.dyna


    def querysetstate(self, s):
        """
        @summary: Update the state without updating the Q-table
        @param s: The new state
        @returns: The selected action
        """
        self.s = s
        action = np.argmax(self.q[s])

        if rand.uniform(0.0, 1.0) <= self.rar:
            action = rand.randint(0, self.num_actions-1)
            self.rar = self.rar * self.radr

        if self.verbose: print "s =", s,"a =",action
        self.a = action
        return action

    def query(self,s_prime,r):
        """
        @summary: Update the Q table and return an action
        @param s_prime: The new state
        @param r: The ne state
        @returns: The selected action
        """

        action = np.argmax(self.q[s_prime])

        self.q[self.s, self.a] = (1 - self.alpha) * self.q[self.s, self.a] + self.alpha * (r + self.gamma * self.q[s_prime, action] )

        if rand.uniform(0.0, 1.0) <= self.rar:
            action = rand.randint(0, self.num_actions-1)
            self.rar = self.rar * self.radr

        if self.verbose: print "s =", s_prime,"a =",action,"r =",r
        self.a = action
        self.s = s_prime
        return action




class Trainer():
    # constructor
    def __init__(self, args):
        self.actionMap = {0: np.NaN, 1:"BUY", 2:"SELL"}
        self.learner = QLearner(args)
        self.para = args

    def getSMA(self, stock, window = 10):
        sma_ind = stock.copy()
        sma = stock.copy()
        size = stock.shape[0]

        for i in range(window-1, size):
            sma[i] = stock[(i-window+1):i].mean()
        sma[:(window-1)] = np.nan
        sma_ind = sma_ind/sma - 1

        return sma_ind, sma

    def getBB(self, stock, sma, window = 10):
        std = stock.copy()
        size = stock.shape[0]
        for i in range(window-1, size):
            std[i] = stock[(i-window+1):i].std()
        std[:window-1] = np.nan

        return (stock - sma)/ 2 / std

    def getEMA(self, stock, sma, window = 10):
        mult = (2 / (window + 1.0))
        ema = (stock - sma) * mult + sma
        return stock/ema - 1, ema

    def transform(self, stock, window = 10):

        sma_ind, sma = self.getSMA(stock, window)
        bb = self.getBB(stock, sma, window)
        ema_ind, ema = self.getEMA(stock, sma, window)

        data = pd.concat((stock,sma_ind, bb, ema_ind), axis=1)
        data.columns = ["OriPrice", "sma_ind", "bb", "ema_ind"]
        return data


    def getTokens(self, indi):
        indi.dropna(inplace=True)
        sma_bins = [np.NINF, -0.06, -0.04, -0.02, -0.01, 0.01, 0.02, 0.03, 0.06, np.PINF]
        smas = pd.cut(indi["sma_ind"], bins = sma_bins, labels = range(1,10))

        bb_bins = [np.NINF, -1.6, -0.9, -0.5, -0.2, 0.2, 0.5, 0.9, 1.6, np.PINF]
        bb = pd.cut(indi["bb"], bins = bb_bins, labels = range(1,10))

        ema_bins = [np.NINF, -0.06,-0.03, -0.02,  -0.01, 0.01, 0.02, 0.03,0.06, np.PINF]
        emas = pd.cut(indi["ema_ind"], bins = ema_bins, labels = range(1,10))

        tokens = bb.astype(str).str.cat(smas.astype(str)).str.cat(emas.astype(str))

        tokenized = pd.concat((tokens, indi["OriPrice"]), axis = 1)
        tokenized.columns = ["tokens", "Price"]

        return tokenized

    def calcReward(self, status, action, dateIndex, data):
        # return reward, next dateIndex
        # print(data.head())
        if status == action == 0:
            return - math.fabs(data.ix[dateIndex + 1, 1]/data.ix[dateIndex, 1] - 1) / 10, dateIndex + 1, action

        if status == 0 and action == 1:
            # if buy
            return data.ix[dateIndex + 1, 1]/data.ix[dateIndex, 1] - 1, dateIndex + 1, action

        if status == 0 and action == 2:
            # if sell
            return 1 - data.ix[dateIndex + 1, 1]/data.ix[dateIndex, 1], dateIndex + 1, action

        if status == 1 and action != 2:
            return data.ix[dateIndex + 1, 1]/data.ix[dateIndex, 1] - 1, dateIndex + 1, 1

        if status == 1 and action == 2:
            return 1 - data.ix[dateIndex + 1, 1]/data.ix[dateIndex, 1], dateIndex + 1, action

        if status == 2 and action != 1:
            return 1 - data.ix[dateIndex + 1, 1]/data.ix[dateIndex, 1], dateIndex + 1, 2

        if status == 2 and action == 1:
            return data.ix[dateIndex + 1, 1]/data.ix[dateIndex, 1] - 1, dateIndex + 1, action

        return 0, dateIndex + 1, 0


    def addEvidence(self, symbol, sd, ed):

        dates = pd.date_range(sd, ed)
        prices_all = ut.readStock(symbol, dates)  # automatically adds SPY
        prices = prices_all[symbol]  # only portfolio symbols
        prices_SPY = prices_all['SPY']  # only SPY, for comparison later

        # print(prices.head())
        indi = self.transform(prices)
        tokens = self.getTokens(indi)

        # if self.verbose: print (tokens["tokens"].describe())

        # print (tokens["tokens"].describe())
        # print tokens.shape

        maxIter = 100
        numIter = 0
        status = 0
        old_total_reward = 0

        # action {0: "nothing", 1:"buy", 2:"sell"}

        while numIter < maxIter:
            total_reward = 0
            dateInd = 0
            numIter += 1
            action = self.learner.querysetstate(int(tokens.iloc[dateInd,0])) #set the state and get first action

            reward, dateInd, status = self.calcReward(status, action, dateInd, tokens)
            total_reward += reward

            while dateInd < tokens.shape[0] - 1:
                action = self.learner.query(int(tokens.iloc[dateInd,0]),reward)
                reward, dateInd, status = self.calcReward(status, action, dateInd, tokens)
                total_reward += reward

            print(total_reward)

            if total_reward == old_total_reward:
                break

            old_total_reward = total_reward


        # example use with new colname
        # volume_all = ut.get_data(syms, dates, colname = "Volume")  # automatically adds SPY
        # volume = volume_all[syms]  # only portfolio symbols
        # volume_SPY = volume_all['SPY']  # only SPY, for comparison later
        # if self.verbose: print volume


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


    def storeModel(self, outfile):
        with open(outfile, 'wb') as output:
            pickle.dump(self.learner, output, pickle.HIGHEST_PROTOCOL)

    def train(self):
        pass