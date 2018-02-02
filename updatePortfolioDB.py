print('Importing modules...', end= " ")
import time, datetime, xlwings as xw, pandas as pd, numpy as np
from datetime import date
import sqlite3
import sys
import matplotlib.pyplot as plt
import logging
print('done.')
try:
    import blpapi
    import portfolio
    from initPortfolio import startSession
    import blpfunctions
    BLOOMBERG = True
except:
    print("Error importing Bloomberg API.")
    BLOOMBERG = False


global book
global sheet
global apikey

apiKey = ['H6B0JP28UDCLN7VT', '1EZ6'] #got 2 to get around rate limiting



#####################################################################################
###################################  MAIN PROGRAM ###################################
#####################################################################################
# bookAddress = str(sys.argv[1])
# DBAddress = str(sys.argv[2])

#delete these and uncomment two lines above to take args, I was being lazy
DBAddress = 'Tracker.db'
bookAddress = r'D:\SSIF\Portfolio-Tracker\portfolio_tracker.xlsm'



#connect to SQLite
conn = sqlite3.connect("Tracker.db")
cursor = conn.cursor()
print("Successfully connected to SQLite database.")

book = xw.Book(bookAddress)
sheet = book.sheets['Transactions']

def updateHoldings():
    #get holding details into dataframe
    sheet = book.sheets['Holding Details']
    try:
        holdings_df = sheet.range('A1').expand('table').options(pd.DataFrame,index=True,header=True).value
        holdings_df.to_sql("Holdings", conn, if_exists='replace')

    except:
        print('error importing holdings dataframe.')
        quit()

def updateTransactions():
    #get transactions into DataFrame
    try:
        transaction_df = sheet.range('A1').expand('table').options(pd.DataFrame,index=True,header=True).value
        buy_sell_df = transaction_df.loc[transaction_df['Transaction Type'].isin(['BUY', 'SELL'])]#filter to buy and sell transactions only
        # convert to SQlite table
        transaction_df.to_sql("Transactions", conn, if_exists='replace')

    except:
        print('error importing transactions dataframe.')
        quit()


def updatePrices():
    s='aaa'




if __name__ == '__main__':
    start_time = time.clock()
    updateHoldings()
    updateTransactions()
    end_time = time.clock()
    total_time = end_time - start_time
    print('total runtime is: ' + str(total_time))
