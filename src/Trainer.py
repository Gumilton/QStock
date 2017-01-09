import numpy as np
import random as rand
import pandas as pd
import util as ut
import pickle
from indicators import transform, getTokens


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

        # if self.verbose: print "s =", s,"a =",action
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

        # if self.verbose: print "s =", s_prime,"a =",action,"r =",r
        self.a = action
        self.s = s_prime
        return action




class Trainer():
    # constructor
    def __init__(self, args):
        self.actionMap = {0: np.NaN, 1:"BUY", 2:"SELL"}
        self.learner = QLearner(args)
        self.para = args

    def calcReward(self, status, action, dateIndex, data):
        # return reward, next dateIndex
        # print(data.head())
        if status == action == 0:
            return - abs(data.ix[dateIndex + 1, 1]/data.ix[dateIndex, 1] - 1) / 10, dateIndex + 1, action

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
        prices_all = ut.readStocks(symbol, dates)  # automatically adds SPY
        prices = prices_all[symbol]  # only portfolio symbols
        prices_SPY = prices_all['SPY']  # only SPY, for comparison later
        # print(prices.head(10))
        # print(prices.head())
        indi = transform(prices)
        tokens = getTokens(indi)
        # print(tokens)
        # if self.verbose: print (tokens["tokens"].describe())

        # print (tokens["tokens"].describe())
        # print tokens.shape

        maxIter = 100
        numIter = 0
        status = 0
        old_total_reward = 0
        ncom = 0
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
                ncom += 1
            else:
                old_total_reward = total_reward
                ncom = 0

            if ncom > 5:
                break


        # example use with new colname
        # volume_all = ut.get_data(syms, dates, colname = "Volume")  # automatically adds SPY
        # volume = volume_all[syms]  # only portfolio symbols
        # volume_SPY = volume_all['SPY']  # only SPY, for comparison later
        # if self.verbose: print volume


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
        orders.ix[:,"Symbol"] = symbol[0]
        orders.ix[:,"Shares"] = 10.0

        dateInd = 0

        while dateInd < tokens.shape[0]:
            action = self.learner.querysetstate(int(tokens.iloc[dateInd,0]))
            orders.iloc[dateInd,1] = self.actionMap[action]
            dateInd += 1

        orders.dropna(inplace=True)
        cleaned = ut.cleanOrders(orders)

        return cleaned


    def storeModel(self, outfile):
        with open(outfile, 'wb') as output:
            pickle.dump(self.learner, output, pickle.HIGHEST_PROTOCOL)

    def loadModel(self, infile):
        with open(infile, 'rb') as input:
            self.learner = pickle.load(input)

    def train(self):
        pass