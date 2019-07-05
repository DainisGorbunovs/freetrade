from typing import Callable

import requests
import json
from datetime import date
# from dateutil import relativedelta, parser
import os
import csv
from collections import OrderedDict
import pandas as pd
import glob
from . import Credentials, Auth, API


class FreeTrade:
    credentials = None

    def __init__(self, email: str, ft_key_file: str = None):
        # no key file given, look for one
        self.credentials = Credentials(ft_key_file)
        self.auth = Auth(self.credentials.get_ft_auth_host(),
                         self.credentials.get_android_verification_api_key(), email)

        self.auth.authenticate()

        self.api = API(self.auth, self.credentials.get_ft_api_host())
        self.assets = {}

    def get_assets_request(self, hits_per_page=30000, page=0) -> requests.Response:
        url = 'https://gbysiom72q-dsn.algolia.net/1/indexes/instruments-v2/browse'
        headers = {
            'Content-Type': 'application/json',
            'X-Algolia-API-Key': self.credentials.get_algolia_api_key(),
            'User-Agent': 'Algolia for Swift (6.1.1); iOS (12.2)',
            'X-Algolia-Application-Id': self.credentials.get_algolia_application_id(),
        }
        data = {
            'params': f'hitsPerPage={hits_per_page}&page={page}&query='
        }
        r = requests.get(url, headers=headers, data=data)

        return r

    def get_assets(self) -> dict:
        if len(self.assets) > 0:
            return self.assets

        r = self.get_assets_request()

        response = json.loads(r.text)['hits']

        assets = {
            'currency': {},
            'exchange': {},
            'asset_class': {},
            'country_of_incorporation': {}
        }
        ticker = {}

        for response_item in response:
            for type in assets.keys():
                if response_item[type] not in assets[type]:
                    assets[type][response_item[type]] = []
                assets[type][response_item[type]].append(response_item)
                ticker[response_item['symbol']] = response_item

        assets['all'] = ticker
        self.assets = assets
        return assets

    def get_tickers(self) -> dict:
        assets = self.get_assets()
        tickers = {}

        for ftmarket, assets in assets['exchange'].items():
            tickers[ftmarket] = []
            for asset in assets:
                tickers[ftmarket].append(asset['symbol'])

        return tickers

    def get_tradingview_tickers(self, join_exchanges: bool = False) -> dict or str:
        tickers = self.get_tickers()
        exchange_name = {
            'XLON': 'LSE',
            'XNYS': 'NYSE',
            'XNAS': 'NASDAQ'
        }

        import_map = {}
        exchange = ''

        append_tickers: Callable[[str, str], str] = lambda ticker: exchange + ':' + ticker
        for ftexchange in tickers.keys():
            exchange = exchange_name[ftexchange]
            import_list = ','.join(map(append_tickers, tickers[ftexchange]))
            import_map[ftexchange] = import_list

        if join_exchanges:
            return ','.join(import_map.values())

        return import_map

    def get_ticker_history_iextrading(self, ticker: str, duration: str = '1m') -> dict:
        raise Exception('Not used anymore. Will be replaced')

    def get_ticker_history_quandl(self, ftexchange: str, ticker: str, start_date: date = None) -> dict:
        raise Exception('Not used anymore. Will be replaced')

    def get_ticker_history(self, ftexchange: str, ticker: str, duration: str = '1m') -> OrderedDict:
        raise Exception('The logic is changed. Will be replaced')

    @staticmethod
    def load_historical_price(ticker: str, directory: str = 'history') -> OrderedDict:
        ticker_file = directory + '/' + ticker + '.csv'
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
        ticker_file = directory + '/' + ticker + '.csv'

        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(ticker_file, 'w') as f:
            w = csv.writer(f)
            w.writerows(prices.items())

    def update_historical_prices(self, directory: str = 'history'):
        assets = self.get_assets()
        for ftmarket, tickerlist in assets['exchange'].items():
            for asset in tickerlist:
                ticker = asset['symbol']
                ticker_file = directory + '/' + ticker + '.csv'

                # load the historical prices
                if os.path.isfile(ticker_file):
                    prices = self.get_ticker_history(ftmarket, ticker, '1m')
                    old_prices = self.load_historical_price(ticker, directory)
                    new_dates = set(prices).difference(old_prices)
                    for history_date in new_dates:
                        old_prices[history_date] = prices[history_date]

                    prices = old_prices
                else:
                    prices = self.get_ticker_history(ftmarket, ticker, '5y')

                # update the file
                self.write_historical_price(prices, ticker, directory)

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
