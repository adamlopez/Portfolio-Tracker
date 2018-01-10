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
import numpy as np
import requests as req
import xlwings as xw
import datetime

import portfolio
import holding
import fx

if BLOOMBERG == True:
    import blpapi
    from blpfunctions import parseCmdLine
    TOKEN_SUCCESS = blpapi.Name("TokenGenerationSuccess")
    TOKEN_FAILURE = blpapi.Name("TokenGenerationFailure")
    AUTHORIZATION_SUCCESS = blpapi.Name("AuthorizationSuccess")
    TOKEN = blpapi.Name("token")
    SESSION_TERMINATED = blpapi.Name("SessionTerminated")



class Engine:
    '''Engine that runs the command line interface and interacts with the portfolio and holding objects accordingly.'''
    def __init__(self, portfolio):
        print("Creating engine...")
        self.rates = fx.RateTable()
        self.portfolio = portfolio


    def run(self):
        '''start the engine in interactive mode from CLI.'''
        active = True
        while active:
            command = input("Please enter a command:")
            actions = self.parse(command)






    def parse(self, command):
        tokens = command.split()
        '''two first tokens specify function to be run - rest of tokens should be treated as arguments for the function.
            returns a tuple of action code and arguments.'''
        for arg in tokens:
            arg = arg.lower()

        if tokens[0] == 'buy':
            if tokens[1] == 'holding':
                newHolding = holding.Holding(*tokens[2:]) #pass all tokens > 1 to holding constructor
                self.portfolio.addholding(newHolding)
                print(newHolding.asSeries())

            elif tokens[1] == 'remove':
                self.portfolio.removeHolding(*tokens[2:])

        elif tokens[0] == "display":
            if tokens[1] == 'holdings':
                print(self.portfolio)



def importPortfolio(DBname):
    '''Initialize the protfolio on application startup.
    Will import all necessary information from database specified in input arguments.'''

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

        hld = holding.Holding(import_prices=False,
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
    port = importPortfolio('Tracker.db')
    eng = Engine(port)
    eng.run()
