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
from datetime import datetime
import holding
import sqlite3
import sys

# import blpapi



# portfolio class. holds a collection of holding objects
class Portfolio:
    def __init__(self, name="DefaultPortfolio", cashBalance=0, holdingsDict=None, baseCurrency='CAD'):
        self.name = name
        self.holdings = holdingsDict
        self.baseCurrency = baseCurrency
        self.cashBalance = cashBalance


    def __repr__(self):
        print('---------------- HOLDINGS ----------------')
        for holding in self.holdings:
            print(holding)

    def addHolding(self, holding):
        self.holdings[holding.ticker] = holding
        self.cashBalance -= holding.getPositionValue()


    def removeHolding(self, ticker):
        for holding in self.holdings:
            if holding.ticker == ticker:
                holdings.remove(holding)


    def getValue(self, startdate=datetime.today(), endDate=datetime.today()):
        total = 0
        if startDate == datetime.today():
            for holding in self.holdings:
                total += holding.getValue()
            return total

        else:
            for holding in self.holdings:
                total += getValue('historical')


    def getCashBalance(self, startdate=datetime.today(), endDate=datetime.today()):
        return cashBalance


    def getSectorWeights(self):
        '''group information by sector, returning a dictionary of weights by sector.'''

        sectorDict = {}
        #populate dictionary with sectors
        for s in self.SECTORS:
            sectorDict[s] = 0

        #make Series of unique sectors for index

        for key, value in self.holdings.items():
            posVal = value.getPositionValue()
            stockSector = value.getSector()
            sectorDict[stockSector] += posVal

        #generate pie plot of sector weightings
        # sector_pie = plt.pie(sector_df['Value ($CAD)'], labels=sector_df.index.values, autopct=None)
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
