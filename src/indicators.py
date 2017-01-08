

import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt

def getSMA(stock, window = 10):
    sma_ind = stock.copy()
    sma = stock.copy()
    size = stock.shape[0]
    for i in range(window-1, size):
        sma[i] = stock[(i-window+1):i].mean()
    sma[:window-1] = np.nan
    sma_ind = sma_ind/sma - 1
    return sma_ind, sma

def getBB(stock, sma, window = 10):
    std = stock.copy()
    size = stock.shape[0]
    for i in range(window-1, size):
        std[i] = stock[(i-window+1):i].std()
    std[:window-1] = np.nan

    return (stock - sma)/ 2 / std

def getEMA(stock, sma, window = 10):
    mult = (2 / (window + 1.0))
    ema = (stock - sma) * mult + sma
    return stock/ema - 1, ema


def getMomentum(stock, window = 10):
    # used for ML training data Y label
    momentum = stock.copy()
    momentum[(window - 1):] = stock[(window - 1):].values / stock[:(stock.shape[0] - window+1)].values - 1
    momentum[:window-1] = np.nan
    return momentum

def transform(stock, window = 10):

    sma_ind, sma = getSMA(stock, window)
    bb = getBB(stock, sma, window)
    ema_ind, ema = getEMA(stock, sma, window)

    # momentum is only used for ML training data Y label
    momentum = getMomentum(stock, window)

    data = pd.concat((stock, stock/stock[0] - 1, sma, sma_ind, bb, ema, ema_ind, momentum), axis=1)
    data.columns = ["OriPrice", "RelPrice", "sma", "sma_ind", "bb", "ema", "ema_ind", "momentum"]
    return data




# if __name__ == "__main__":
#     sym = "IBM"
#     start_date = dt.datetime(2006, 1, 1)
#     end_date = dt.datetime(2009, 12, 31)
#
#     data = get_data([sym], dates=pd.date_range(start_date, end_date))
#
#     stock = data[sym]
#
#     ext = transform(stock)
#
#     smaplot = ext[["OriPrice", "sma", "sma_ind"]]
#     plot = smaplot.plot()
#     fig = plot.get_figure()
#     fig.savefig('SMA.png')
#     smaplot = ext[["RelPrice", "sma", "sma_ind"]]
#     smaplot.ix[:,"sma"] = smaplot.ix[:,"sma"]/smaplot.ix[9,"sma"] - 1
#     smaplot.ix[:,"sma_ind"] = smaplot.ix[:,"sma_ind"] * 3
#     plot = smaplot.plot()
#     fig = plot.get_figure()
#     fig.savefig('SMA_adjusted.png')
#
#
#     bbplot = ext[["OriPrice", "bb"]]
#     plot = bbplot.plot()
#     fig = plot.get_figure()
#     fig.savefig('bbplot.png')
#     bbplot = ext[["RelPrice", "bb"]]
#     bbplot.ix[:,"bb"] = bbplot.ix[:,"bb"]/ 4
#     plot = bbplot.plot()
#     fig = plot.get_figure()
#     fig.savefig('bbplot_adjusted.png')
#
#     emaplot = ext[["OriPrice", "ema", "ema_ind"]]
#     plot = emaplot.plot()
#     fig = plot.get_figure()
#     fig.savefig('EMA.png')
#     emaplot = ext[["RelPrice", "ema", "ema_ind"]]
#     emaplot.ix[:,"ema"] = emaplot.ix[:,"ema"]/emaplot.ix[9,"ema"] - 1
#     emaplot.ix[:,"ema_ind"] = emaplot.ix[:,"ema_ind"] * 3
#     plot = emaplot.plot()
#     fig = plot.get_figure()
#     fig.savefig('EMA_adjusted.png')
#
#     # ext.to_csv("extracted_indicators.csv")



