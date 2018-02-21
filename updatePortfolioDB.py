import time, datetime, xlwings as xw, pandas as pd, numpy as np
from datetime import date
import sqlite3
import sys
import matplotlib.pyplot as plt
import logging
import price_query

#####################################################################################
###################################  MAIN PROGRAM ###################################
#####################################################################################


#connect to SQLite
DBAddress = 'Tracker.db'
conn = sqlite3.connect(DBAddress)
cursor = conn.cursor()
print("Successfully connected to SQLite database.")


def updateHoldings():
    try:
        allHoldings = pd.read_sql("SELECT * from Holdings", conn)
        holdings_df.to_sql("Holdings", conn, if_exists='replace')

    except:
        print('error importing holdings dataframe.')
        quit()

def updateTransactions():
    transaction_df = pd.read_csv('transactions.csv', encoding='latin1', index_col='ID')
    transaction_df.to_sql("Transactions", conn, if_exists='replace')

def updatePrices():
    allTransactions = pd.read_sql("SELECT * from Transactions", conn)
    tickers = allTransactions['Symbol'].unique()
    master_price_df = pd.DataFrame(data=[],columns=['open','high','low','close','adjusted close','volume','dividend amount','split coefficient','symbol'])

    for ticker in tickers:
        df = price_query.daily_prices(ticker)
        master_price_df = master_price_df.append(df)


    master_price_df.to_sql("Prices", conn, if_exists='replace')




if __name__ == '__main__':
    start_time = time.clock()
    updateTransactions()
    # updatePrices()
    updateHoldings()
    end_time = time.clock()
    total_time = end_time - start_time
    print('Database updated successfully.')
    print('total runtime: ' + str(total_time))
