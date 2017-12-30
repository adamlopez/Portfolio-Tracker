# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 12:08:42 2017

@author: adamlopez
"""
import requests as req
import pandas as pd
import numpy as np
import dash
import portfolio_tracker
import time
import datetime
# import blpapi


class Holding:
    '''used to identify a stock that was owned at some point in time.
       In order to support fractional buying and selling, a transaction ledger is used.'''
    def __init__(self, ticker=None, domicile='US', transaction_df=None):
        self.ticker = ticker
        self.domicile = domicile
        self.price_df  = portfolio_tracker.get_daily_price_timeseries_alphavantage(ticker, outputsize='full')
        self.__transaction_df = transaction_df


    def getCurrentPrice(self):
        return self.price_df['5. adjusted close'].iloc[-1]

    def getSharesOutstanding(self):
        '''return current number of shares outstanding based on transaction dataframe. Assumes purchase quantities are positive and sale quantities are negative.'''
        print (self.__transaction_df['Quantity'])
        
        return self.__transaction_df['Quantity'].astype(float).sum()

    def getCurrentValue(self):
        return self.getCurrentPrice() * self.getSharesOutstanding()

    def update(self, timeOutput=False):
        startTime = time.clock()
        print("updating " + self.ticker + "...", end = " ")
        self.price_df  = portfolio_tracker.get_daily_price_timeseries_alphavantage(self.ticker, outputsize='full')
        endTime = time.clock()

    def getTransactions(self):
        return __transaction_df

        if timeOutput == False:
            print('done.')
        else:
            print("done. ({} seconds elapsed)".format(endTime - startTime))

    def commit(self, conn, ifExists='replace'):
        '''save all holding-specific information to the database. Only reason to use this is to make sure the transaction dataframe gets saved properly.'''
