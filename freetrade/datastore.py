import csv
import glob
import os
from collections import OrderedDict
from datetime import datetime
from itertools import chain

import pandas as pd
from dateutil.relativedelta import relativedelta

from freetrade import API, Index


class DataStore:
    def __init__(self, api: API, index: Index):
        self.api = api
        self.index = index

    @staticmethod
    def load_historical_price(ticker: str, directory: str = 'history') -> OrderedDict:
        ticker_file = directory + os.sep + ticker + '.csv'
        old_prices = OrderedDict()
        with open(ticker_file, 'r') as f:
            r = csv.reader(f)
            for line in r:
                history_date, history_price = line
                history_price = float(history_price)
                old_prices[history_date] = history_price
        return old_prices

    @staticmethod
    def write_historical_price(prices: OrderedDict, ticker: str, directory: str = 'history'):
        ticker_file = directory + os.sep + ticker + '.csv'

        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(ticker_file, 'w') as f:
            w = csv.writer(f)
            w.writerows(prices.items())

    @staticmethod
    def load_historical_data_as_dataframe(directory: str = 'history') -> pd.DataFrame:
        files = glob.glob(f'{directory}/*.csv')
        if len(files) == 0:
            return pd.DataFrame()

        dm = pd.read_csv(files[0], header=None)
        for file in files[1:]:
            df = pd.read_csv(file, header=None)
            dm = dm.merge(df, how='outer', on=0)

        dm.columns = ['Date'] + list(map(lambda x: x[8:-4], files))
        dm.set_index('Date', inplace=True)
        dm.sort_index(inplace=True)

        return dm

    def update_historical_prices(self, directory: str = 'history'):
        assets = self.index.get_assets()

        for ftmarket, tickerlist in assets['exchange'].items():
            for asset in tickerlist:
                ticker = asset['symbol']
                ticker_file = directory + os.sep + ticker + '.csv'

                # load the historical prices
                if os.path.isfile(ticker_file):
                    old_prices = self.load_historical_price(ticker, directory)
                    last_date_str = next(reversed(old_prices))  # YYYY-MM-DD: str
                    last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
                    relative_delta = relativedelta(datetime.now(), last_date)

                    duration = '1m'
                    if relative_delta.years >= 2:
                        duration = '5y'
                    elif relative_delta.years >= 1:
                        duration = '2y'
                    elif relative_delta.months >= 6:
                        duration = '1y'
                    elif relative_delta.months >= 3:
                        duration = '6m'
                    elif relative_delta.months >= 1:
                        duration = '3m'

                    fetched_prices = self.api.get_ticker_history(ticker, ftmarket, duration)
                    prices = OrderedDict(chain(old_prices.items(), fetched_prices.items()))
                else:
                    prices = self.api.get_ticker_history(ticker, ftmarket, '5y')

                # update the file
                self.write_historical_price(prices, ticker, directory)
