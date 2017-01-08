import pandas as pd
import numpy as np
import os


def getWebStock():
    pass

def readStocks(symbols, dates, addSPY=True, colname = 'Adj Close'):
    """Read stock data (adjusted close) for given symbols from CSV files."""
    df = pd.DataFrame(index=dates)
    if addSPY and 'SPY' not in symbols:  # add SPY for reference, if absent
        symbols = ['SPY'] + symbols

    for symbol in symbols:
        df_temp = pd.read_csv(symbol_to_path(symbol), index_col='Date',
                parse_dates=True, usecols=['Date', colname], na_values=['nan'])
        df_temp = df_temp.rename(columns={colname: symbol})
        df = df.join(df_temp)
        # if symbol == 'SPY':  # drop dates SPY did not trade
        #     df = df.dropna(subset=["SPY"])

    return df


def symbol_to_path(symbol, base_dir=os.path.join("..", "dat")):
    """Return CSV file path given ticker symbol."""
    return os.path.join(base_dir, "{}.csv".format(str(symbol)))


def compute_portvals(orders, start_date, end_date, start_val = 100000):
    # this is the function the autograder will call to test your code
    # TODO: Your code here

    stocks = orders.Symbol.unique().tolist()

    # In the template, instead of computing the value of the portfolio, we just
    # read in the value of IBM over 6 months
    prices = readStocks(stocks, pd.date_range(start_date, end_date))
    prices = prices[stocks]  # remove SPY

    # inner join to remove invalid dates
    orders = orders.join(prices,  how = "inner")[['Symbol', 'Order',  'Shares']]

    # flip the trade sign of shares
    orders.loc[orders.Order == "SELL", "Shares"] = - orders.loc[orders.Order == "SELL", "Shares"]

    prices["cash"] = 1

    # temp = pd.DataFrame(0, index = prices.index, columns=["cash"])

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

