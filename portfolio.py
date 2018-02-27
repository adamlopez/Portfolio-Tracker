# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 12:20:56 2017

@author: adamlopez
"""
import requests as req
import pandas as pd
import dash
import numpy as np
import datetime
import sqlite3
import sys

import holding, fx

''' portfolio class. holds a collection of holding objects '''

class Portfolio:
    def __init__(self, name="DefaultPortfolio", cashBalance=0, holdingsDict=None, baseCurrency='CAD'):
        self.name = name
        self.holdings = holdingsDict
        self.baseCurrency = baseCurrency
        self.cashBalance = cashBalance
        self.RateTable = fx.RateTable() # most recent forex rates

        # for caching summary data tables
        self.holdings_df = None
        self.sectorDict = None


    def __repr__(self):
        for holding in self.holdings.values():
            print(holding + " " + holding.getSharesOutstanding())


    def addHolding(self, holding):
        self.holdings[holding.ticker] = holding
        self.cashBalance -= holding.getPositionValue()

    def removeHolding(self, ticker):
        for holding in self.holdings:
            if holding.ticker == ticker:
                holdings.remove(holding)

    def getHoldings(self):
        if self.holdings_df is None:
            outputDF = pd.DataFrame()
            for ticker,holding in self.holdings.items():
                s = holding.asSeries()
                outputDF = outputDF.append(s)
            self.holdings_df = outputDF

        else:
            outputDF = self.holdings_df

        print(outputDF['Position Value'].sum())
        return outputDF



    def getValue(self, startdate=datetime.datetime.today(), endDate=datetime.datetime.today()):
        '''returns historical portfolio values in timeseries format.'''
        total = 0


    def getCashBalance(self, startdate=datetime.datetime.today(), endDate=datetime.datetime.today()):
        return cashBalance


    def getSectorWeights(self):
        '''group information by sector, returning a dictionary of weights by sector.'''
        if self.sectorDict == None:
            sectorDict = {}
            #populate dictionary with sectors
            for s in self.SECTORS:
                sectorDict[s] = 0

            #make Series of unique sectors for index

            for key, holding in self.holdings.items():
                posVal = holding.getValue(value='integer')
                print(key, posVal)
                stockSector = holding.sector
                sectorDict[stockSector] += posVal

            #generate pie plot of sector weightings
            # sector_pie = plt.pie(sector_df['Value ($CAD)'], labels=sector_df.index.values, autopct=None)
            self.sectorValues = sectorDict
            sectorSummaryDF = pd.DataFrame.from_dict(data=sectorDict,orient='index',columns=['Sector Value ($CAD)'])
            # sectorSummaryDF.rename({0:'Sector Value ($CAD)'}, axis='columns', inplace=True)
            print(sectorSummaryDF)
            quit()
            sectorSummaryDF['%% of total portfolio'] = sectorSummaryDF['Sector Value ($CAD)']/sectorSummaryDF['Sector Value ($CAD)'].sum()

            print("total portfolio value: {sectorSummaryDF['Sector Value ($CAD)'].sum()}")

            self.total_value = sectorSummaryDF['Sector Value ($CAD)'].sum()

            print(sectorSummaryDF)

            quit()

        return sectorDict


    #Bloomberg tickers for sector-specific benchmark indicdes
    BENCHMARKS = {
        'US':{
            'S5CONS Index': { 'name': 'Cons. Disc.' },
            'S5COND Index': { 'name': 'Cons. Staples' },
            'S5INFT Index': { 'name': 'Technology' },
            'S5ENRS Index': { 'name': 'Energy' },
            'S5FINL Index': { 'name': 'Financials' },
            'S5MATR Index': { 'name': 'Materials' },
            'S5HLTH Index': { 'name': 'Healthcare' },
            'S5INDU Index': { 'name': 'Industrials' },
            'S5UTIL Index': { 'name': 'Utilities' },
        },
        'CN': {
            'STCONS Index': { 'name': 'Cons. Disc.' },
            'STCOND Index': { 'name': 'Cons. Staples' },
            'STINFT Index': { 'name': 'Technology' },
            'STENRS Index': { 'name': 'Energy' },
            'STFINL Index': { 'name': 'Financials' },
            'STMATR Index': { 'name': 'Materials' },
            'STHLTH Index': { 'name': 'Healthcare' },
            'STINDU Index': { 'name': 'Industrials' },
            'STUTIL Index': { 'name': 'Utilities' },
        }
    }

    SECTORS = ['Cons. Disc.',
               'Cons. Staples',
               'Technology',
               'Energy',
               'Financials',
               'Healthcare',
               'Industrials',
               'Utilities']

if __name__ == "__main__":
    quit()
