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
# import blpapi


class Holding:
    '''used to identify a stock that was owned at some point in time.
       In order to support fractional buying and selling, a transaction ledger is implemented.'''
    def __init__(self, ticker=None, name=None, domicile='US', currency='USD', transaction_df=None, sector=None, manager=None, import_prices=True):
        self.ticker = ticker
        self.domicile = domicile
        self.currency = currency
        self.name = name
        if import_prices == True:
            self.price_df = price_query.get_daily_price_timeseries_alphavantage(ticker, outputsize='full')
        else:
            self.price_df = None

        self.__transaction_df = transaction_df
        self.sector = sector
        self.manager = manager

    def __repr__(self):
        return str(self.name + " Position size: " + str(self.getSharesOutstanding()))


    def getCurrentPrice(self):
        try:
            return self.price_df['5. adjusted close'].iloc[-1].astype('float')
        except:
            return "Error pulling price from dataframe."

    def getSharesOutstanding(self):
        '''returns timeseries of historical shares outstanding for the holding.'''

        # filter down to buy and sell transactions
        transactions = self.__transaction_df.loc[self.__transaction_df['Transaction Type'].isin(['BUY', 'SELL'])]
        transactions.set_index(transactions['Transaction Date'], inplace=True) #sort by transaction date
        transactions.index = pd.to_datetime(transactions.index)

        output = pd.DataFrame(data=None, index=self.price_df.index, columns=['Share Count'])
        output['Share Count'] = transactions['Transaction Quantity'].cumsum()

        output['Share Count'][0] = 0  #make position value on first day of index
        output['Share Count'].fillna(method='ffill', inplace=True)
        output = output.apply(pd.Series)
        return output



    def getValue(self, requestedCurrency, start_date=datetime.datetime(2005,1,1)):
        '''returns holding value in timeseries format.'''
        shareCount = self.getSharesOutstanding()

        closePrices = self.price_df['5. adjusted close'].astype('float64')
        rates = fx.RateTable().getRateSeries(self.currency, 'CAD')
        convertedCloses = closePrices.multiply(rates).apply(pd.Series).fillna(method='ffill')

        print(type(closePrices))
        print(type(shareCount))
        print(type(convertedCloses))
        shareCount = shareCount.apply(pd.Series)
        convertedCloses = convertedCloses.apply(pd.Series)
        output = pd.DataFrame({'convertedCloses':convertedCloses, 'shareCount':shareCount}, index=shareCount.index)
        print(output)


        return output


    def getTransactions(self):
        return __transaction_df


    def update(self, timeOutput=False):
        startTime = time.clock()
        print("updating " + self.ticker + "...", end = " ")
        self.price_df  = price_query.get_daily_price_timeseries_alphavantage(self.ticker, outputsize='full')
        if timeOutput == False:
            endTime = time.clock()
            print('done.')
        else:
            endTime = time.clock()
            print("done. ({} seconds elapsed)".format(endTime - startTime))

    def commit(self, conn, ifExists='replace'):
        '''save all holding-specific information to the database. Only reason to use this is to make sure the transaction dataframe gets saved properly.'''


if __name__ == "__main__":
    #initialize SQLdb connection
    conn = sqlite3.connect('Tracker.db')
    cursor = conn.cursor()

    print("importing transactions...", end = " ")
    master_transaction_df = pd.read_sql("SELECT * from Transactions", conn)
    print("done.")

    ticker = 'AAPL'
    stockTransactions = master_transaction_df.loc[master_transaction_df['Symbol'].isin([ticker])]

    h = Holding(ticker='AAPL', name='Apple', domicile='US', currency='USD', transaction_df=stockTransactions, sector='Technology', manager=None, import_prices=True)
    print(h.getValue('USD'))
