import time, datetime, pandas as pd, numpy as np
from datetime import date
import sqlite3
import sys
import logging
import price_query


def updateHoldings():
    try:
        allHoldings = pd.read_sql("SELECT * from Holdings", conn)
        holdings_df.to_sql("Holdings", conn, if_exists='replace')

    except:
        print('error importing holdings dataframe.')
        quit()

def updateTransactions(path):
    transaction_df = pd.read_csv(path, encoding='latin1', index_col='ID')
    transaction_df.to_sql("Transactions", conn, if_exists='replace')
    return transaction_df

def updatePrices():
    allTransactions = pd.read_sql("SELECT * from Transactions", conn)
    tickers = allTransactions['Symbol'].unique()
    master_price_df = pd.DataFrame(data=[],columns=['open','high','low','close','adjusted close','volume','dividend amount','split coefficient','symbol'])

    for ticker in tickers:
        df = price_query.daily_prices(ticker)
        master_price_df = master_price_df.append(df)


    master_price_df.to_sql("Prices", conn, if_exists='replace')
    return master_price_df


if __name__ == '__main__':
    start_time = time.clock()

    #connect to SQLite
    conn = sqlite3.connect('Tracker.db')
    print("Successfully connected to SQLite database.")


    transDF = updateTransactions('transactions.csv')
    PriceDF = updatePrices()
    end_time = time.clock()
    total_time = end_time - start_time
    print('Database updated successfully.')
    print('total runtime: ' + str(total_time))
