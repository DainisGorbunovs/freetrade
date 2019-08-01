import json
from typing import Callable

import requests

from freetrade import Credentials


class Index:
    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.assets = {}
        self.host = 'https://{}-dsn.algolia.net'.format(credentials.get_algolia_application_id().lower())

    def get_assets_request(self, hits_per_page=30000, page=0) -> requests.Response:
        url = self.host + '/1/indexes/' + self.credentials.get_algolia_index_name() + '/browse'
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
