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
    def __init__(self, ticker=None, name=None, domicile='US', transaction_df=None, sector=None, manager=None, import_prices=True):
        self.ticker = ticker
        self.domicile = domicile
        self.name = name
        if import_prices == True:
            self.price_df  = portfolio_tracker.get_daily_price_timeseries_alphavantage(ticker, outputsize='full')

        self.__transaction_df = transaction_df
        self.sector=sector
        self.manager=manager

    def __repr__(self):
        return str(self.name + " Position size: " + str(self.getSharesOutstanding()))


    def getCurrentPrice(self):
        if True:
            return 80
        return self.price_df['5. adjusted close'].iloc[-1].astype('float')

    def getSharesOutstanding(self):
        '''return current number of shares outstanding based on transaction dataframe. Assumes purchase quantities are positive and sale quantities are negative.'''
        return float(self.__transaction_df['Transaction Quantity'].sum())

    def getPositionValue(self):
        return self.getCurrentPrice() * self.getSharesOutstanding()

    def getTransactions(self):
        return __transaction_df

    def getSector(self):
        return self.sector

    def update(self, timeOutput=False):
        startTime = time.clock()
        print("updating " + self.ticker + "...", end = " ")
        self.price_df  = portfolio_tracker.get_daily_price_timeseries_alphavantage(self.ticker, outputsize='full')
        if timeOutput == False:
            endTime = time.clock()
            print('done.')
        else:
            endTime = time.clock()
            print("done. ({} seconds elapsed)".format(endTime - startTime))



    def commit(self, conn, ifExists='replace'):
        '''save all holding-specific information to the database. Only reason to use this is to make sure the transaction dataframe gets saved properly.'''

if __name__ == "__main__":
    quit()
