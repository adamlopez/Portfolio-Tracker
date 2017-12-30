import requests as req
import time
import datetime
import pandas as pd
import numpy as np
import csv
import urllib3
from datetime import date, timedelta
import zipfile
import io

def unzipURL(url):
    '''unzips file found at url, returning an infolist object of the files extracted.'''

    try:
        r = req.get(str(url))
    except:
        return "error retrieving data from url provided."

    z = zipfile.ZipFile(io.BytesIO(r.content))
    return z.namelist()



def getForexTable(url,position=0, index='Date'):
    info = unzipURL(url)
    # print(info)
    forexdf =  pd.read_csv(info[position], index_col=index)
    return forexdf


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

if __name__ == '__main__':
    ECBURL = r"https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip?82a3f6f1218fcfac4242624c0b826f50"

    df = getForexTable(ECBURL)
    print(df)
    quit()
    print(get_cad_forex('USD',date.today()-timedelta(weeks=52) ,date.today()))
