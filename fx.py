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
        self._masterDF =  pd.read_csv(zipFile.open(name), index_col='Date', parse_dates=True)



    def getRateTable(self):
        return self._masterDF

    def getRateSeries(self, priceCurrency, baseCurrency):
        '''cross-rate calculation based on ECB rate publication. Returns a series with exchange rates of daily price/base rates.'''
        table = self.getRateTable()

        EURToPrice = table[priceCurrency]
        EURToBase = table[baseCurrency]

        BaseToEUR = 1/EURToBase

        #cross-rate conversion
        PriceToBase = EURToPrice.multiply(BaseToEUR)
        PriceToBase.rename("{}/{}".format(baseCurrency, priceCurrency), inplace=True)

        return PriceToBase


    def convert(self, amount, priceCurrency, baseCurrency, date=date.today()):
        '''convert value at most recent exchange rate available.'''
        rates = self.getRateSeries(priceCurrency, baseCurrency)

        try:
            dayRate = rates[date]
        except KeyError:
            print('No rate information for {} available'.format(date.strftime("%Y-%m-%d")))
            quit()

        return amount * dayRate


if __name__ == '__main__':
    quit()
