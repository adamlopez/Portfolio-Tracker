import sys
import sqlite3
import pandas as pd
import numpy as np
import datetime

import portfolio
import holding
import fx
import initPortfolio


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


        elif tokens[0] == "display":
            if tokens[1] == 'holdings':
                print(self.portfolio.getHoldings())

            elif tokens[1] == 'sectors':
                print(self.portfolio.getSectorWeights())

            elif tokens[1] == 'transactions':
                print(self.portfolio.holdings[tokens[2]].transaction_df)


if __name__ == "__main__":
    print('app is run using the initPortfolio script.')
    quit()
