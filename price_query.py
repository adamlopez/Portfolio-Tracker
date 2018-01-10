print('Importing modules...', end= " ")
import time, datetime, xlwings as xw, pandas as pd, numpy as np
from datetime import date
import sqlite3
import sys
import matplotlib.pyplot as plt
import logging
print('done.')
try:
    import blpapi
    import portfolio
    from initPortfolio import startSession
    import blpfunctions
    BLOOMBERG = True
except:
    print("Error importing Bloomberg API.")
    BLOOMBERG = False


global book
global sheet
global apiKey

apiKey = ['H6B0JP28UDCLN7VT', '1EZ6'] #got 2 to get around rate limiting
def get_daily_price_timeseries_alphavantage(symbol,outputsize='compact', timer=True):
    """returns a dataframe of historical stock prices for symbol inputted.
    second (optional) input modifies date range called for. possible values for second input are full (returns all stock-specific daily price data available) and compact (last 30 days only)."""

    # print('fetching prices for ' + symbol)

    if timer == True:
        startTime = time.clock()
        print(f'pulling prices for {symbol}...', end=" ")

    function = 'TIME_SERIES_DAILY_ADJUSTED'
    try:
        key = apiKey[0]

        stock_info_url = 'http://www.alphavantage.co/query?function=' + function + '&symbol=' + symbol + '&apikey=' + key + '&outputsize='+str(outputsize)
        # print(stock_info_url)
        json_df = pd.read_json(stock_info_url, orient='columns')
    except:
        key = apiKey[1]
        stock_info_url = 'http://www.alphavantage.co/query?function=' + function + '&symbol=' + symbol + '&apikey=' + key + '&outputsize='+str(outputsize)

        # print(stock_info_url)
        json_df = pd.read_json(stock_info_url, orient='columns')


    price_df = pd.DataFrame(data=json_df['Time Series (Daily)'])

    price_df = price_df['Time Series (Daily)'].apply(pd.Series)
    price_df.iloc[::-1] #invert df date order

    price_df.drop(['5. Time Zone', '4. Output Size', '3. Last Refreshed','2. Symbol', '1. Information'], axis=0, inplace=True) #drop unneccessary rows from JSON output

    price_df.drop(0, axis=1, inplace=True) #drop empty column from JSON output

    price_df.index = pd.to_datetime(price_df.index) #format index as datetime object

    np.round(price_df.index.astype(np.int64), -9).astype('datetime64[ns]') #truncate datetime to day value

    endTime = time.clock()
    if timer == True:
        print(f'Done. ({endTime-startTime} seconds.)')

    return  price_df
