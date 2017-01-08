import pandas as pd
import os
import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt

def getWebStock(startyear, startmonth, startday, endyear, endmonth, endday, stockname):
    start = datetime.datetime(startyear,startmonth,startday)
    end = datetime.datetime(endyear,endmonth,endday)
    stock = web.DataReader(stockname, 'yahoo', start, end)
    stock.to_csv('stockname.csv')


def plotstockhistory(startyear, startmonth, startday, endyear, endmonth, endday, stockname):
    start = datetime.datetime(startyear,startmonth,startday)
    end = datetime.datetime(endyear,endmonth,endday)
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


