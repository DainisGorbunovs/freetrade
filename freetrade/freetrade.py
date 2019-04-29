from typing import Callable

import requests
import json


class FreeTrade:
    API_KEY = ''
    APP_ID = ''
    USER_AGENT = 'Algolia for Swift (6.1.1); iOS (12.2)'
    HEADERS = dict()

    def __init__(self, api_key: str, app_id: str):
        self.assets = dict()
        self.API_KEY = api_key
        self.APP_ID = app_id

        self.HEADERS = {
            'Content-Type': 'application/json',
            'X-Algolia-API-Key': self.API_KEY,
            'User-Agent': self.USER_AGENT,
            'X-Algolia-Application-Id': self.APP_ID,
        }

    def get_assets_request(self) -> requests.Response:
        url = 'https://gbysiom72q-dsn.algolia.net/1/indexes/instruments-v2/browse'
        headers = self.HEADERS
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

        for response_item in response:
            for type in assets.keys():
                if response_item[type] not in assets[type]:
                    assets[type][response_item[type]] = []
                assets[type][response_item[type]].append(response_item)

        assets['all'] = response
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

    def get_ticker_history(self, ticker: str, duration: str = '5y'):
        # FreeTrade uses API from IEX trading to get price history
        # https://iextrading.com/developer/docs/#chart
        # duration: 5y, 2y, 1y, ytd, 6m, 3m, 1m, 1d

        url = f'https://api.iextrading.com/1.0/stock/{ticker}/chart/{duration}'

        response = requests.get(url)

        history = json.loads(response.text)
        return history

    def get_etfs(self):
        assets = self.get_assets()
        return assets['asset_class']['ETF']
