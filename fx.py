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

class RateTable:
    def __init__(self):
        self.update()


    def update(self):
        url = r"https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip?82a3f6f1218fcfac4242624c0b826f50"

        try:
            r = req.get(str(url))
            zipFile = zipfile.ZipFile(io.BytesIO(r.content))

        except:
            return "error retrieving data from {}.".format(url)

        name = zipFile.namelist()[0]
        self.masterDF =  pd.read_csv(zipFile.open(name), index_col='Date')



    def getRateTable(self):
        return self.masterDF

    def getRateSeries(self, priceCurrency, baseCurrency):
        '''cross-rate calculation based on ECB rate publication. Returns a series with exchange rates of daily price/base rates.'''
        table = self.getRateTable()
        print(table['USD'], table['CAD'])
        EURToPrice = table[priceCurrency]
        EURToBase = table[baseCurrency]
        BaseToEUR = 1/EURToBase
        print(BaseToEUR)
        PriceToBase = EURToPrice.multiply(BaseToEUR)
        return PriceToBase
        #cross-rate conversion


def getFXValue(priceCurrency, baseCurrency, value):
    '''convert value at most recent exchange rate available.'''
    getFXTable()


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
