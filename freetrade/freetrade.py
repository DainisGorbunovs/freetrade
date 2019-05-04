from typing import Callable

import requests
import json
from datetime import date
from dateutil import relativedelta, parser
import os
import csv
from collections import OrderedDict


class FreeTrade:
    API_KEY = ''
    APP_ID = ''
    QUANDL_API_KEY = ''
    ALGOLIA_HEADERS = {}
    QUANDL_HEADERS = {}

    def __init__(self, api_key: str, app_id: str, quandl_api_key: str):
        self.assets = dict()
        self.API_KEY = api_key
        self.APP_ID = app_id
        self.QUANDL_API_KEY = quandl_api_key

        self.ALGOLIA_HEADERS = {
            'Content-Type': 'application/json',
            'X-Algolia-API-Key': self.API_KEY,
            'User-Agent': 'Algolia for Swift (6.1.1); iOS (12.2)',
            'X-Algolia-Application-Id': self.APP_ID,
        }

        self.QUANDL_HEADERS = {
            'Content-Type': 'application/json',
            'User-Agent': 'Freetrade/2.4.1 (io.freetrade.freetrade; build:773; iOS 12.2.0) Alamofire/4.8.0',
        }

    def get_assets_request(self) -> requests.Response:
        url = 'https://gbysiom72q-dsn.algolia.net/1/indexes/instruments-v2/browse'
        headers = self.ALGOLIA_HEADERS
        data = {
            'params': 'hitsPerPage=30000&page=0&query='
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
        # Does not support securities from LSE (London Stock Exchange)

        # FreeTrade uses API from IEX trading to get price history
        # https://iextrading.com/developer/docs/#chart
        # duration: 5y, 2y, 1y, ytd, 6m, 3m, 1m, 1d
        url = f'https://api.iextrading.com/1.0/stock/{ticker}/chart/{duration}'

        response = requests.get(url)

        return None if response.status_code != 200 else json.loads(response.text)

    def get_ticker_history_quandl(self, ftexchange: str, ticker: str, start_date: date = None) -> dict:
        if start_date is None:
            start_date = date.today() - relativedelta.relativedelta(months=1)

        start_date_str = start_date.strftime('%Y-%m-%d')
        ticker = ticker.replace('.', '_')

        url = f'https://www.quandl.com/api/v3/datasets/{ftexchange}/{ticker}?' \
            f'api_key={self.QUANDL_API_KEY}&column_index=4&order=asc&start_date={start_date_str}'

        response = requests.get(url, headers=self.QUANDL_HEADERS)

        return None if response.status_code != 200 else json.loads(response.text)

    def get_ticker_history(self, ftexchange: str, ticker: str, duration: str = '1m') -> OrderedDict:
        # duration: 5y, 2y, 1y, ytd, 6m, 3m, 1m, 1d

        if ftexchange == 'XLON':
            history_date = date.today()
            delta_times = {
                '5y': relativedelta.relativedelta(years=5),
                '2y': relativedelta.relativedelta(years=2),
                '1y': relativedelta.relativedelta(years=1),
                'ytd': relativedelta.relativedelta(month=1, day=1),
                '6m': relativedelta.relativedelta(months=6),
                '3m': relativedelta.relativedelta(months=3),
                '1m': relativedelta.relativedelta(months=1),
                '1d': relativedelta.relativedelta(days=1),
            }
            if duration in delta_times:
                history_date -= delta_times[duration]
            else:
                history_date = parser.parse(duration)

            history = self.get_ticker_history_quandl('XLON', ticker, history_date)
            data = OrderedDict((history_date, price)
                               for history_date, price in history['dataset']['data'])
        else:
            history = self.get_ticker_history_iextrading(ticker, duration)
            data = OrderedDict((price['date'], price['close'])
                               for price in history)

        return data

    @staticmethod
    def load_historical_price(ticker: str, directory: str = 'history'):
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

