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
from datetime import datetime
import holding

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

    book = xw.Book('D:/SSIF/Portfolio-Tracker/portfolio_tracker.xlsm')
    sheet = book.sheets['MSFT Transactions']
    transaction_df = sheet.range('A1').expand('table').options(pd.DataFrame,index=True,header=True).value

    #initialize SQLdb connection
    conn = sqlite3.connect(DBname)
    cursor = conn.cursor()

    print('creating holdings...')
    MSFT = holding.Holding('MSFT', transaction_df=transaction_df, domicile='US')
    holdings = {'MSFT':MSFT}

    print('creating portfolio...')
    port = portfolio.Portfolio('SSIFCAD', holdings, 'CAD')

    print('MSFT current price:' + port.holdings['MSFT'].getCurrentPrice())
    # port.holdings['MSFT'].update(timeOutput=True)
    print('MSFT shares outstanding: ' + port.holdings['MSFT'].getSharesOutstanding())




    quit()

    print("importing transactions...", end = " ")
    transaction_df = pd.read_sql("SELECT * from Transactions", conn)
    print("done.")

    print("importing holdings...", end = " ")
    holdings_df = pd.read_sql("SELECT * from Holdings", conn)
    print("done.")





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
    importPortfolio(sys.argv[1])
