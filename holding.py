# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 12:08:42 2017

@author: adamlopez
"""
import requests as req
import pandas as pd
import numpy as np
import dash
import time
import datetime
import sqlite3

import price_query
import fx

class Holding:
    '''used to identify a stock that was owned at some point in time.
       In order to support fractional buying and selling, a transaction ledger is implemented.'''
    def __init__(self, ticker=None, name=None, domicile='US', currency='USD', transaction_df=None, sector=None, manager=None, price_df=None):
        self.ticker = ticker
        self.domicile = domicile
        self.currency = currency
        self.name = name
        self.sector = sector
        self.manager = manager
        self.transaction_df = transaction_df
        self.price_df = price_df

        self.share_series = None

        # to deal with cash accounts
        if 'cash account' in self.name.lower():
            self.isCashAcct = True
        else:
            self.isCashAcct = False

    def __repr__(self):
        '''replace the print operator for the holding class.'''
        return str(f"{self.getSharesOutstanding(value='integer')} shares of {self.name}")

    def asSeries(self):
        ''' Returns a holding object in series form. Particularly useful for concatenating with other holdings.'''
        s = pd.Series(data={'Name':self.name,
                              'Ticker':self.ticker,
                              'Sector':self.sector,
                              'Domicile':self.domicile,
                              'Currency':self.currency,
                              'Price': self.getCurrentPrice(),
                              'Shares Outstanding':self.getSharesOutstanding(value='integer'),
                              'Position Value':self.getValue(value='integer'),
                             })
        s.name = self.ticker
        return s


    def getCurrentPrice(self, currency=None):
        '''returns most recent price available.'''

        currency = self.currency
        try:
            value = self.price_df.loc[self.price_df.index.max(), 'adjusted close']

        except TypeError: #will be raised by any holdings without prices (implemented for cash accts)
            value = 0

        converted = fx.globalRateTable.convert(value,priceCurrency='CAD',baseCurrency=self.currency)

        return value


    def getSharesOutstanding(self,value='timeseries'):
        '''returns timeseries of historical shares outstanding for the holding.'''

        #return empty dataframe if the holding is a cash account
        if self.isCashAcct == True:
            if value == 'timeseries':
                return pd.DataFrame(data=None, index=pd.date_range(start=datetime.datetime(2007,1,1), end=pd.Timestamp.today()))

            elif value == 'integer':
                return 0

        if self.share_series is None:
            # filter to buy and sell transactions
            transactions = self.transaction_df.loc[self.transaction_df['Type'].isin(['BUY','SELL'])]
            transactions.set_index(transactions['Transaction Date'], inplace=True) #sort by transaction date

            transactions.index = pd.to_datetime(transactions.index)

            output = pd.DataFrame(data=None, index=self.price_df.index, columns=['Share Count'])
            output.index = pd.to_datetime(output.index)
            output['Share Count'] = transactions['Quantity'].cumsum()
            output['Share Count'][0] = 0  #make position value 0 on first day of index
            output['Share Count'].fillna(method='ffill', inplace=True)
            output = output.apply(pd.Series)
            self.share_series = output

        if value == 'timeseries':
            # print(output)
            return self.share_series
        elif value == 'integer': #return most recent value
            return self.share_series.loc[output.index.max(), 'Share Count']



    def getValue(self, requestedCurrency='CAD', start_date=datetime.datetime(2007,1,1),value='timeseries'):
        '''returns holding value in timeseries format.'''

        if self.isCashAcct == True:
            transactions = self.transaction_df
            transactions.set_index(transactions['Transaction Date'], inplace=True) #sort by transaction date
            transactions.index = pd.to_datetime(transactions.index)

            output = pd.DataFrame(data=None, index=pd.date_range(start=datetime.datetime(2007,1,1), end=pd.Timestamp.today()))
            output['Position Value'] = transactions['Settlement Amount'].cumsum()
            output['Position Value'][0] = 0  #make position value 0 on first day of index
            output['Position Value'].fillna(method='ffill', inplace=True)
            output.index = pd.to_datetime(output.index)
            output = output.apply(pd.Series)
            output = output['Position Value']

        else:
            shareCount = self.getSharesOutstanding()
            rates = fx.RateTable().getRateSeries(requestedCurrency, self.currency)
            closePrices = self.price_df['adjusted close'].astype('float64')
            closePrices.index = pd.to_datetime(closePrices.index)

            convertedCloses = closePrices.multiply(rates).apply(pd.Series).fillna(method='ffill').apply(pd.Series)
            output = convertedCloses[0].multiply(shareCount['Share Count'])

        if value == 'timeseries':
            return output
        elif value == 'integer': #return most recent value
            return output.loc[output.index.max()]


    def getTransactions(self):
        return transaction_df


    def update(self, timeOutput=False):
        startTime = time.clock()
        print("updating " + self.ticker + "...", end = " ")
        self.price_df  = price_query.daily_prices(self.ticker, outputsize='full')
        if timeOutput == True:
            endTime = time.clock()
            print("done. ({} seconds elapsed)".format(endTime - startTime))
        else:
            endTime = time.clock()
            print('done.')

    def commit(self, conn, ifExists='replace'):
        '''save all holding-specific information to the database. Only reason to use this is to make sure the transaction dataframe gets saved properly.'''


if __name__ == "__main__":
    #initialize SQLdb connection
    conn = sqlite3.connect('Tracker.db')
    cursor = conn.cursor()

    print("importing transactions...", end = " ")
    master_transaction_df = pd.read_sql("SELECT * from Transactions", conn)
    print("done.")
    master_price_df = pd.read_sql("SELECT * from Prices", conn,index_col=['timestamp','symbol'])
    print(master_price_df)
    quit()
    ticker = 'AAPL'

    stockTransactions = master_transaction_df.loc[master_transaction_df['Symbol'].isin([ticker])]
    prices = master_price_df.loc[master_price_df['symbol'].isin([ticker])]
    print(prices)
    quit()
    h = Holding(ticker=ticker, name='Apple', domicile='US', currency='USD', transaction_df=stockTransactions, sector='Technology', price_df=prices)
    print(h.getValue())
