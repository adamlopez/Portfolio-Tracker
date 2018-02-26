# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 14:25:34 2017

@author: adamlopez
"""

import sys
import sqlite3
import pandas as pd
import numpy as np
import datetime

import engine
import portfolio
import holding
import fx



def importPortfolio(DBname, import_prices=True):
    '''Initialize the protfolio on application startup.
    Will import all necessary information from database specified in input arguments.'''

    #initialize SQLdb connection
    conn = sqlite3.connect(DBname)
    cursor = conn.cursor()

    print("importing transactions...", end = " ")
    master_transaction_df = pd.read_sql("SELECT * from Transactions", conn, index_col=['ID'])
    print("done.")

    print("importing prices...", end = " ")
    master_price_df = pd.read_sql("SELECT * from Prices", conn,index_col=['index'])
    print("done.")

    print('creating holdings...', end = " ")
    holdings_df = pd.read_sql("SELECT * from Holdings", conn)
    print('done.')



    #create dictionary of holding objects
    holdingsDict={}
    for index,row in holdings_df.iterrows():
        name = row.loc['Ticker']

        prices = master_price_df.loc[master_price_df['symbol'].isin([name])]
        prices.index = pd.to_datetime(prices.index)
        stockTransactions = master_transaction_df.loc[master_transaction_df['Symbol'].isin([name])]

        hld = holding.Holding(price_df=prices,
                       ticker=row.loc['Ticker'],
                       name=row.loc['Company'],
                       domicile=row.loc['Country of Origin'],
                       currency=row.loc['Currency'],
                       sector=row.loc['Sector'],
                       manager=row.loc['Manager'],
                       transaction_df = stockTransactions)
        holdingsDict[name] = hld
        print(f'{name} instantiated.')

    port = portfolio.Portfolio('SSIFCAD', holdingsDict=holdingsDict, baseCurrency='CAD')
    conn.close()
    return port


if __name__ == "__main__":
    port = importPortfolio('Tracker.db')
    eng = engine.Engine(port)
    eng.run()
