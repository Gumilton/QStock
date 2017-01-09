import pandas as pd
import numpy as np
import os
import pandas_datareader.data as web
import datetime as dt
import matplotlib.pyplot as plt

def getWebStock(stockSym, startDate = "2001-1-1", verbose = False):
    # start = dt.datetime(startyear,startmonth,startday)
    # end = dt.datetime(endyear,endmonth,endday)
    stock = web.DataReader(stockSym, 'yahoo', start=startDate)
    stock.to_csv(os.path.join("..", "dat", "stocks", "{}.csv".format(str(stockSym) + "_" + str(dt.date.today()))))
    if verbose:
        print(stockSym + " is updated by " + str(dt.date.today()))


def plotstockhistory(startyear, startmonth, startday, endyear, endmonth, endday, stockname):
    start = dt.datetime(startyear,startmonth,startday)
    end = dt.datetime(endyear,endmonth,endday)
    stock = web.DataReader(stockname, 'yahoo', start, end)
    stockadjclose = stock["Adj Close"]

    plt.figure()
    stockadjclose.plot()
    plt.show()

def readStocks(symbols, dates, addSPY=True, colname = 'Adj Close'):
    """Read stock data (adjusted close) for given symbols from CSV files."""
    df = pd.DataFrame(index=dates)
    if addSPY and 'SPY' not in symbols:  # add SPY for reference, if absent
        symbols = ['SPY'] + symbols

    allStocksFiles = getAllStockFileName()
    for symbol in symbols:
        if symbol in allStocksFiles:
            df_temp = pd.read_csv(os.path.join("..", "dat", "stocks", allStocksFiles[symbol]), index_col='Date',
                    parse_dates=True, usecols=['Date', colname], na_values=['nan'])
            df_temp = df_temp.rename(columns={colname: symbol})
            df = df.join(df_temp)
            # if symbol == 'SPY':  # drop dates SPY did not trade
            #     df = df.dropna(subset=["SPY"])

    return df.dropna()

def getAllStockFileName():
    return {file.split("_")[0]:file for file in os.listdir(os.path.join("..", "dat", "stocks"))}



# def symbol_to_path(symbol, base_dir=os.path.join("..", "dat", "stocks")):
#     """Return CSV file path given ticker symbol."""
#     return os.path.join(base_dir, "{}.csv".format(str(symbol)))


def compute_portvals(orders, start_date, end_date, start_val = 100000):
    # this is the function the autograder will call to test your code

    stocks = orders.Symbol.unique().tolist()
    prices = readStocks(stocks, pd.date_range(start_date, end_date))
    prices = prices[stocks]  # remove SPY

    # inner join to remove invalid dates
    orders = orders.join(prices,  how = "inner")[['Symbol', 'Order',  'Shares']]

    # flip the trade sign of shares
    orders.loc[orders.Order == "SELL", "Shares"] = - orders.loc[orders.Order == "SELL", "Shares"]

    prices["cash"] = 1

    trades = pd.pivot_table(orders, values = "Shares", index = orders.index, columns = "Symbol", aggfunc=np.sum)
    trades = trades[prices.columns[:-1]]
    trades = trades.join(pd.DataFrame(0, index = prices.index, columns=["cash"]), how="outer")
    trades.fillna(0, inplace=True)
    trades.cash = (- prices * trades).sum(axis = 1)

    holdings = pd.DataFrame(0, index = trades.index, columns=trades.columns)
    holdings.iloc[0,-1] = start_val

    temp = trades.iloc[0,:] + holdings.iloc[0,:]
    invest = prices.iloc[0,:] * temp
    if (np.abs(invest[:-1])).sum() / invest.sum() <= 3.0:
        holdings.iloc[0,:] = temp

    for i in range(1,holdings.shape[0]):
        temp = trades.iloc[i,:] + holdings.iloc[i - 1,:]
        invest = prices.iloc[i,:] * temp
        if (np.abs(invest[:-1])).sum() / invest.sum() <= 3.0:
            holdings.iloc[i,:] = temp
        else:
            holdings.iloc[i,:] = holdings.iloc[i - 1,:]

    portvals = (prices * holdings).sum(axis = 1)
    return pd.DataFrame(portvals)

def getLoyal3List():
    stocks = pd.read_csv(os.path.join("..", "doc", "loyal3_availability.csv"))["Sym."].values
    stocks = np.core.defchararray.replace(stocks.astype("str"), ".", "-")
    return list(stocks)

def cleanOrders(orders):

    # one buy one sell
    indices = [0]
    status = orders.iloc[0, 1]
    for i in range(1, orders.shape[0]):
        newStatus = orders.iloc[i, 1]
        if newStatus == status:
            continue
        else:
            indices.append(i)
            status = newStatus
    #
    cleanOrders = orders.iloc[indices, :]
    if cleanOrders.iloc[0, 1] == "SELL":
        cleanOrders = cleanOrders.iloc[1:, :]


    # # allow multiple buys but single sell
    # indices = [0]
    # # orders.iloc[0,2] = 500
    # status = orders.iloc[0, 1]
    # for i in range(1, orders.shape[0]):
    #     newStatus = orders.iloc[i, 1]
    #     if newStatus == status == "SELL":
    #         continue
    #     else:
    #         indices.append(i)
    #         status = newStatus
    #
    #         # orders.iloc[0,2] = 500
    # shares = 0
    # for j in range(0, cleanOrders.shape[0]):
    #     if cleanOrders.iloc[j,1] == "BUY":
    #         shares += cleanOrders.iloc[j,2]
    #     else:
    #         cleanOrders.iloc[j, 2] = shares
    #         shares = 0

    return cleanOrders