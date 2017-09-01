import requests as req, time, datetime, pandas as pd, numpy as np, csv, urllib3
from datetime import date, timedelta

def get_cad_forex( foreignCurrency, start_date, end_date, CADbase=True):
    '''returns timeseries of daily exchange rates for any currency against the CAD. (source: Bank of Canada)'''

    #format currency pair string
    if CADbase ==True:
        pair = foreignCurrency + 'CAD'
    else:
        pair = 'CAD' + foreignCurrency

    #force dates to proper string format
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    url = r'http://www.bankofcanada.ca/valet/observations/FX{}/json?start_date={}&end_date={}'.format(pair, start_str, end_str)

    df = pd.read_csv(url,header=7, parse_dates=True)

    # df['dates'] = [row(0) for row in df.index]
    # df.drop(labels=[2,3,4,5,6,7,8], axis=1, inplace=True) #drop irrelevant columns
    # df.drop(labels=[0,1,2,3,4,5,6,7,8], axis=0, inplace=True) #drop irrelevant rows

    #extract price timeseries
    # series = pd.Series(data=df.columns(1))

    return df

def main():
    print(get_cad_forex('USD',date.today()-timedelta(weeks=52) ,date.today()))

if __name__ == '__main__':
    main()
