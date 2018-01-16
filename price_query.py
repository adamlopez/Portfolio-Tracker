print('Importing modules...', end= " ")
import time, datetime, xlwings as xw, pandas as pd, numpy as np, requests as req
from datetime import date
import sqlite3
import sys
import matplotlib.pyplot as plt
import logging
import json
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

apiKey = [ '1EZ6', 'H6B0JP28UDCLN7VT', "48OQ3ZIV043PD00C"] #got 2 to get around rate limiting

def batch_prices(symbolList, provider="Alphavantage", timer=True):
    ''' fetches all the most recent prices for the symbolist provided in dictionary format.
    example query: https://www.alphavantage.co/query?function=BATCH_STOCK_QUOTES&symbols=MSFT,FB,AAPL&apikey=demo'''
    function = "BATCH_STOCK_QUOTES"
    symbols = ','.join(symbolList)

    # try:
    queryURL = f"https://www.alphavantage.co/query?function={function}&symbols={symbols}&apikey={apiKey[0]}"
    r = req.get(queryURL)
    df = json.loads(r.text)
    df = pd.DataFrame(df['Stock Quotes'])
    df.rename(columns= {'1. symbol' : 'symbol',
                        '2. price': 'close',
                        '3. volume': 'volume',
                        '4. timestamp' : 'timestamp'}, inplace=True)
    df.index=pd.to_datetime(df['timestamp'], infer_datetime_format=True)
    df.drop(labels=['timestamp'], inplace=True, axis=1)
    return df

    # except:
        # print('error importing batch prices.')
        # quit()



def daily_prices(symbol, provider='Alphavantage',outputsize='full', timer=True):
    """returns a dataframe of historical stock prices for symbol inputted.
    second (optional) input modifies date range called for. possible values for second input are full (returns all stock-specific daily price data available) and compact (last 30 days only)."""

    # print('fetching prices for ' + symbol)

    if timer == True:
        startTime = time.clock()
        print(f'pulling prices for {symbol}...')

    function = 'TIME_SERIES_DAILY_ADJUSTED'
    try:
        key = apiKey[0]
        stock_info_url = 'http://www.alphavantage.co/query?function=' + function + '&symbol=' + symbol + '&apikey=' + key + '&outputsize='+str(outputsize)
        json_df = pd.read_json(stock_info_url, orient='columns')

    except:
        try:
            print('first key failed, trying second key.')
            key = apiKey[1]
            stock_info_url = 'http://www.alphavantage.co/query?function=' + function + '&symbol=' + symbol + '&apikey=' + key + '&outputsize='+str(outputsize)
            json_df = pd.read_json(stock_info_url, orient='columns')

        except:
            print('second key failed, trying third key.')
            key = apiKey[1]
            stock_info_url = 'http://www.alphavantage.co/query?function=' + function + '&symbol=' + symbol + '&apikey=' + key + '&outputsize='+str(outputsize)
            json_df = pd.read_json(stock_info_url, orient='columns')

    price_df = pd.DataFrame(data=json_df['Time Series (Daily)'])

    price_df = price_df['Time Series (Daily)'].apply(pd.Series)
    price_df.iloc[::-1] #invert df date order

    price_df.drop(['5. Time Zone', '4. Output Size', '3. Last Refreshed','2. Symbol', '1. Information'], axis=0, inplace=True) #drop unneccessary rows from JSON output
    price_df.index.names=['timestamp']
    price_df.rename(columns= {'1. open' : 'open',
                              '2. high': 'high',
                              '3. low': 'low',
                              '4. close' : 'close',
                              '5. adjusted close': 'adjusted close',
                              '6. volume': 'volume',
                              '7. dividend amount': 'dividend amount',
                              '8. split coefficient': 'split coefficient'},
                              inplace=True)


    price_df.drop(0, axis=1, inplace=True) #drop empty column from JSON output
    price_df['symbol'] = symbol
    price_df.index = pd.to_datetime(price_df.index) #format index as datetime object
    np.round(price_df.index.astype(np.int64), -9).astype('datetime64[ns]') #truncate datetime to day value

    if timer == True:
        endTime = time.clock()
        print(f'Done. ({endTime-startTime} seconds.)\n')

    return  price_df


if __name__ == "__main__":

    symbols=['AAPL', 'RY', 'CVS', 'WFC', 'MEQ','GNTX', 'L','TSLA']
    conn = sqlite3.connect("Tracker.db")
    cursor = conn.cursor()

    newPrices = batch_prices(symbols)
    AAPL = daily_prices(symbols[0])
    print(AAPL)
    AAPL.to_sql("Prices", conn, if_exists='replace')

    newPrices.to_sql("Prices", conn, if_exists='append')
