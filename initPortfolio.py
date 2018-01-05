# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 14:25:34 2017

@author: adamlopez
"""
global BLOOMBERG
BLOOMBERG = False

from optparse import OptionParser, OptionValueError
import threading
import sys
import sqlite3
import pandas as pd
import portfolio
import requests as req
import dash
import numpy as np
import datetime
import holding
import fx
import xlwings as xw

if BLOOMBERG == True:
    import blpapi
    from blpfunctions import parseCmdLine
    TOKEN_SUCCESS = blpapi.Name("TokenGenerationSuccess")
    TOKEN_FAILURE = blpapi.Name("TokenGenerationFailure")
    AUTHORIZATION_SUCCESS = blpapi.Name("AuthorizationSuccess")
    TOKEN = blpapi.Name("token")
    SESSION_TERMINATED = blpapi.Name("SessionTerminated")

def importPortfolio(DBname):
    """Initialize the protfolio on application startup.
    Will import all necessary information from database specified in input arguments.
    """

    # book = xw.Book('D:/SSIF/Portfolio-Tracker/portfolio_tracker.xlsm')
    # sheet = book.sheets['MSFT Transactions']
    # transaction_df = sheet.range('A1').expand('table').options(pd.DataFrame,index=True,header=True).value

    #initialize SQLdb connection
    conn = sqlite3.connect(DBname)
    cursor = conn.cursor()

    print("importing transactions...", end = " ")
    master_transaction_df = pd.read_sql("SELECT * from Transactions", conn)
    print("done.")

    print('creating holdings...', end = " ")
    holdings_df = pd.read_sql("SELECT * from Holdings", conn)
    print('done.')


    #create dictionary of holding objects
    holdingsDict={}
    for index,row in holdings_df.iterrows():
        name = row.loc['Ticker']
        stockTransactions = master_transaction_df.loc[master_transaction_df['Symbol'].isin([name])]

        hld =  holding.Holding(import_prices=False,
                               ticker=row.loc['Ticker'],
                               name=row.loc['Company'],
                               domicile=row.loc['Country of Origin'],
                               sector=row.loc['Sector'],
                               manager=row.loc['Manager'],
                               transaction_df = stockTransactions)
        holdingsDict[name] = hld

    port = portfolio.Portfolio('SSIFCAD', holdingsDict=holdingsDict, baseCurrency='CAD')
    return port






def startSession(args):
    #BLOOMBERG BOILERPLATE
    options = parseCmdLine()
    #Fill SessionOptions
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost(options.host)
    sessionOptions.setServerPort(options.port)
    print("Connecting to %s:%s" % (options.host, options.port))
    session = blpapi.Session(sessionOptions)

    # Start a Session
    if not session.start():
        print("Failed to start session.")
        return

    return session



if __name__ == "__main__":
    port = importPortfolio(sys.argv[1])
    url = r"https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip?82a3f6f1218fcfac4242624c0b826f50"
    rates = fx.RateTable()
    print(rates.getRateSeries('CAD', 'USD'))
    print(rates.convert(100, 'CAD', 'USD'))
