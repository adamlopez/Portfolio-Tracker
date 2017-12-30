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
    def __init__(self, name, holdingsDict=None, baseCurrency='CAD'):
        self.name = name
        self.holdings = holdingsDict
        self.baseCurrency = baseCurrency


    def printHoldings(self):
        for holding in holdings:
            print(holding.ticker)

    def addHolding(self, holding):
        self.holdings[holding.ticker] = holding


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


    def getCashBal(self, startdate=datetime.today(), endDate=datetime.today()):
        print("Cash balance")
        return 100

    def calculate_sector_weights(self, holdings_df):
        """group information by sector, returning a dataframe of weights by sector."""

        #make Series of unique sectors for index
        unique_sectors = pd.Series(holdings_df.Sector.unique())

        sector_df = pd.DataFrame(data=None, index=unique_sectors, columns=['Value ($CAD)', 'Value (%)'])

        #calculate sector $ values
        for sector in unique_sectors:
            sector_df.loc[sector,'Value ($CAD)'] = holdings_df.loc[holdings_df['Sector'] == sector,'Total Value ($CAD)'].sum()

        portfolio_value = sector_df['Value ($CAD)'].sum()

        #generate pie plot of sector weightings
        # sector_pie = plt.pie(sector_df['Value ($CAD)'], labels=sector_df.index.values, autopct=None)
        return sector_df



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

if __name__ == "__main__":
    quit()
    # use for testing basic portfolio-specific functionality
