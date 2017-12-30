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
global apikey

apiKey = ['H6B0JP28UDCLN7VT', '1EZ6'] #got 2 to get around rate limiting

def get_daily_price_timeseries_alphavantage(symbol,outputsize='compact', time=False):
    """returns a dataframe of historical stock prices for symbol inputted.
    second (optional) input modifies date range called for. possible values for second input are full (returns all stock-specific daily price data available) and compact (last 30 days only)."""

    # print('fetching prices for ' + symbol)

    function = 'TIME_SERIES_DAILY_ADJUSTED'
    try:
        key = apiKey[0]

        stock_info_url = 'http://www.alphavantage.co/query?function=' + function + '&symbol=' + symbol + '&apikey=' + key + '&outputsize='+str(outputsize)
        json_df = pd.read_json(stock_info_url, orient='columns')
    except:
        key = apiKey[1]
        stock_info_url = 'http://www.alphavantage.co/query?function=' + function + '&symbol=' + symbol + '&apikey=' + key + '&outputsize='+str(outputsize)
        json_df = pd.read_json(stock_info_url, orient='columns')

    price_df = pd.DataFrame(data=json_df['Time Series (Daily)'])

    price_df = price_df['Time Series (Daily)'].apply(pd.Series)
    price_df.iloc[::-1] #invert df date order

    price_df.drop(['5. Time Zone', '4. Output Size', '3. Last Refreshed','2. Symbol', '1. Information'], axis=0, inplace=True) #drop unneccessary rows from JSON output

    price_df.drop(0, axis=1, inplace=True) #drop empty column from JSON output

    price_df.index = pd.to_datetime(price_df.index) #format index as datetime object

    np.round(price_df.index.astype(np.int64), -9).astype('datetime64[ns]') #truncate datetime to day value
    return  price_df



#####################################################################################
###################################  MAIN PROGRAM ###################################
#####################################################################################

def main():
    book = xw.Book(r'D:\SSIF\Portfolio-Tracker\portfolio_tracker.xlsm')
    sheet = book.sheets['Dashboard']
    stoploss = sheet.range('E5').value
    last_refresh = sheet.range('E20').value
    stock_count = sheet.range('E4').value

    #support bloomberg price data pull - NOT IMPLEMENTED YET
    if BLOOMBERG:
        session  = startSession(sys.argv)
        startDate = "20171205"
        prices = blpfunctions.getHistorical(session, ["AAPL US EQUITY", "AMZN US EQUITY"],["PX_LAST", "PE_RATIO"], startDate)
        # Stop the session
        session.stop()
        return


    #connect to SQLite
    conn = sqlite3.connect("Tracker.db")
    cursor = conn.cursor()
    print("Successfully connected to SQLite database.")


    #get transactions into DataFrame
    sheet = book.sheets['Transactions']
    try:
        transaction_df = sheet.range('A1').expand('table').options(pd.DataFrame,index=True,header=True).value
        buy_sell_df = transaction_df.loc[transaction_df['Transaction Type'].isin(['BUY', 'SELL'])]#filter to buy and sell transactions only
        # convert to SQlite table
        transaction_df.to_sql("Transactions", conn, if_exists='replace')

    except:
        print('error importing transactions dataframe.')
        quit()

    # table = cursor.execute("SELECT * from Transactions")
    # rows = cursor.fetchall()
    # for row in rows:
    #     print(row)


    #get holding details into dataframe
    sheet = book.sheets['Holding Details']
    try:
        holdings_df = sheet.range('A1').expand('table').options(pd.DataFrame,index=True,header=True).value
        holdings_df.to_sql("Holdings", conn, if_exists='replace')

    except:
        print('error importing holdings dataframe.')
        quit()



    #get cash balances into dataFrame
    sheet = book.sheets['Cash Rec']
    try:
        cash_df = sheet.range('A1').expand('table').options(pd.DataFrame,index=True,header=True).value
    except:
        print('error importing cash dataframe.')
        quit()
    # plt.show()

    #################################### get stock values ###################################

    #group transactions by symbol
    transaction_group = buy_sell_df.groupby('Symbol')


    originalStockList = buy_sell_df['Symbol'].unique()

    # originalStockList = ['AAPL', 'RY']
    originalStockList= holdings_df['Ticker']



    for stock in originalStockList:
        price_timeseries = get_daily_price_timeseries_alphavantage(stock, outputsize='full')
        # price_timeseries = price_timeseries.iloc[::-1] #sort dates from most to least recent


        # add running total of shares owned
        g = transaction_group.get_group(stock) #make object holding transaction for specific stock
        g.set_index(g['Transaction Date'], inplace=True) #sort by transaction date
        price_timeseries['Shares Bought/Sold'] = g['Transaction Quantity'] #add stocks transactions to price dataframe

        #create running total columns of shares owned
        price_timeseries['Position Size'] = price_timeseries['Shares Bought/Sold'].cumsum()
        price_timeseries['Position Size'][0] = 0 #make position value on first day of index 0
        price_timeseries['Position Size'].fillna(method='ffill', inplace=True)
        price_timeseries.drop('Shares Bought/Sold', axis=1, inplace=True)


        #convert price values to float object
        price_timeseries['5. adjusted close'] = pd.to_numeric(price_timeseries['5. adjusted close'])

        #compute total position values
        price_timeseries['Position Value'] = price_timeseries[['5. adjusted close', 'Position Size']].product(axis=1)

        price_timeseries.columns = pd.MultiIndex.from_product([[stock], price_timeseries.columns])
        master_price_df = master_price_df.join(price_timeseries, how='outer')


    ################################### CALCULATE PORTFOLIO RETURN ###################################
    print(master_price_df.xs('Position Value', axis=1, level=1))
    master_price_df['Total Equity Value'] = master_price_df.xs('Position Value', axis=1, level=1).sum(axis=1)
    print(master_price_df['Total Equity Value'])

    #paste dataframe to sheet
    sheet = book.sheets['Prices']
    sheet.clear()
    #DELETE THIS LATER TO PULL LIVE PRICE DATA
    # master_price_df = sheet.range('A1').expand('table').options(pd.DataFrame,index=True,header=True).value
    sheet.range('A1').value = master_price_df


    ###################################  REFRESH EXCEL METADATA ###################################
    sheet = book.sheets['Dashboard']
    last_refresh = date.today()
    sheet.range('E20').value = [last_refresh] #update last refresh time


if __name__ == '__main__':
    start_time = time.clock()
    main()
    end_time = time.clock()
    total_time = end_time - start_time
    print('total runtime is: ' + str(total_time))


#Brent's list
# 3 criteria: stock return, weightings, no sector weight over 35, no 3 over 30%, I don't think dividends work properly
# stock price & dividend tracking
# index tracking index dividend tracking
# track CAD and USD
# stop loss at 20% below 52-day high


# phase 2
# KPI tracking:
# tracking different indicators for different stocks
#ex: watch P/E if it gets above 20x trigger warning

#attribution:
# did we pick the right stocks or the wrong stocks in each sector
