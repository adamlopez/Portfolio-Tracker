print('importing modules...')
import requests as req, json, time, datetime, pprint, xlwings as xw, pandas as pd, numpy as np, collections, time, matplotlib.pyplot as plt
from datetime import date
from fx import get_cad_forex
global book
global sheet



def get_daily_price_timeseries_alphavantage(symbol,outputsize='compact'):
    """returns a dictionary of historical stock prices for symbol inputted.
    second (optional) input modifies date range called for. possible values for second input are full (returns all stock-specific daily price data available) and compact (last 30 days only)."""
    function = 'TIME_SERIES_DAILY_ADJUSTED'
    stock_info_url = 'http://www.alphavantage.co/query?function=' + function + '&symbol=' + symbol + '&apikey=1EZ6' + '&outputsize='+str(outputsize)
    json_df = pd.read_json(stock_info_url, orient='columns')
    price_df = pd.DataFrame(data=json_df['Time Series (Daily)'])
    price_df = price_df['Time Series (Daily)'].apply(pd.Series)
    price_df.iloc[::-1]
    return  price_df


#####################################################################################
###################################  MAIN PROGRAM ###################################
#####################################################################################

def main():
    book = xw.Book(r'C:/Users/Adam/Google Drive/school/The Fund/portfolio-tracker/portfolio_tracker.xlsm')
    sheet = book.sheets['Dashboard']
    stoploss = sheet.range('E5').value
    last_refresh = sheet.range('E20').value
    stock_count = sheet.range('E4').value

    #get transactions into DataFrame
    sheet = book.sheets['Transactions']
    try:
        transaction_df = sheet.range('A1').expand('table').options(pd.DataFrame,index=True,header=True).value
        buy_sell_df = transaction_df.loc[transaction_df['Type'].isin(['BUY', 'SELL'])]#filter to buy and sell transactions only
    except:
        print('error importing transactions dataframe.')
        quit()

    #get holding details into dataframe
    sheet = book.sheets['Holding Details']
    try:
        holdings_df = sheet.range('A1').expand('table').options(pd.DataFrame,index=True,header=True).value
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
    ################################### group information by sector ###################################

    #make Series of unique sectors for index
    unique_sectors = pd.Series(holdings_df.Sector.unique())

    sector_df = pd.DataFrame(data=None, index=unique_sectors, columns=['Value ($CAD)', 'Value (%)'])

    #calculate sector $ values
    for sector in unique_sectors:
        sector_df.loc[sector,'Value ($CAD)'] = holdings_df.loc[holdings_df['Sector'] == sector,'Total Value ($CAD)'].sum()

    portfolio_value = sector_df['Value ($CAD)'].sum()

    #generate pie plot of sector weightings
    sector_pie = plt.pie(sector_df['Value ($CAD)'], labels=sector_df.index.values, autopct=None)
    # plt.show()

    #################################### get stock values ###################################

    #group transactions by symbol
    transaction_group = buy_sell_df.groupby('Symbol')


    originalStockList = buy_sell_df['Symbol'].unique()

    # originalStockList = ['AAPL', 'RY']
    originalStockList= holdings_df['Ticker']


    #generate business day index for days since fund's inception
    start = datetime.datetime(2007,1,1)
    end = datetime.datetime.today()
    # base_headers = ['1. open', '2. high', '3. low', '4. close', '5. adjusted close', '6. volume', '7. dividend amount', '8. split coefficient']
    headers=[]

    master_price_df  = pd.DataFrame(data=None, columns = [[],[]])

    for stock in originalStockList:
        print('fetching prices for {}'.format(stock))
        price_timeseries = get_daily_price_timeseries_alphavantage(stock, outputsize='full')
        # price_timeseries = price_timeseries.iloc[::-1] #sort dates from most to least recent
        price_timeseries.drop(['5. Time Zone', '4. Output Size', '3. Last Refreshed','2. Symbol', '1. Information'], axis=0, inplace=True) #drop unneccessary rows from JSON output
        price_timeseries.drop(0, axis=1, inplace=True) #drop empty column from JSON output
        price_timeseries.index = pd.to_datetime(price_timeseries.index) #format index as datetime object
        np.round(price_timeseries.index.astype(np.int64), -9).astype('datetime64[ns]') #truncate datetime to day value


        # add running total of shares owned
        g = transaction_group.get_group(stock) #make object holding transaction for specific stock
        g.set_index(g['Transaction Date'], inplace=True) #sort by transaction date
        price_timeseries['Shares Bought/Sold'] = g['Quantity'] #add stocks transactions to price dataframe

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
    sheet.range('E20').value = last_refresh #update last refresh time


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
