

import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt


def getSMA(stock, window=10):
    sma_ind = stock.copy()
    # print(sma_ind.head())
    sma = stock.copy()
    size = stock.shape[0]

    for i in range(window - 1, size):
        sma.iloc[i, 0] = stock.iloc[(i - window + 1):i, 0].mean()
    sma.iloc[:(window - 1), 0] = np.nan
    sma_ind = sma_ind / sma - 1
    # print(sma_ind.head(20))
    return sma_ind, sma


def getBB(stock, sma, window=10):
    std = stock.copy()
    size = stock.shape[0]
    for i in range(window - 1, size):
        std.iloc[i, 0] = stock.iloc[(i - window + 1):i, 0].std()
    std.iloc[:window - 1, 0] = np.nan

    return (stock - sma) / 2 / std


def getEMA(stock, sma, window=10):
    mult = (2 / (window + 1.0))
    ema = (stock - sma) * mult + sma
    return stock / ema - 1, ema


def transform(stock, window=10):
    sma_ind, sma = getSMA(stock, window)
    bb = getBB(stock, sma, window)
    ema_ind, ema = getEMA(stock, sma, window)
    # print(bb)
    data = pd.concat((stock, sma_ind, bb, ema_ind), axis=1)
    # print(data)
    data.columns = ["OriPrice", "sma_ind", "bb", "ema_ind"]
    return data


def getTokens(indi):
    indi.dropna(inplace=True)
    sma_bins = [np.NINF, -0.06, -0.04, -0.02, -0.01, 0.01, 0.02, 0.03, 0.06, np.PINF]
    smas = pd.cut(indi["sma_ind"], bins=sma_bins, labels=range(1, 10))

    bb_bins = [np.NINF, -1.6, -0.9, -0.5, -0.2, 0.2, 0.5, 0.9, 1.6, np.PINF]
    bb = pd.cut(indi["bb"], bins=bb_bins, labels=range(1, 10))

    ema_bins = [np.NINF, -0.06, -0.03, -0.02, -0.01, 0.01, 0.02, 0.03, 0.06, np.PINF]
    emas = pd.cut(indi["ema_ind"], bins=ema_bins, labels=range(1, 10))

    tokens = bb.astype(str).str.cat(smas.astype(str)).str.cat(emas.astype(str))

    tokenized = pd.concat((tokens, indi["OriPrice"]), axis=1)
    tokenized.columns = ["tokens", "Price"]

    return tokenized


def getMomentum(stock, window = 10):
    # used for ML training data Y label
    momentum = stock.copy()
    momentum[(window - 1):] = stock[(window - 1):].values / stock[:(stock.shape[0] - window+1)].values - 1
    momentum[:window-1] = np.nan
    return momentum

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



