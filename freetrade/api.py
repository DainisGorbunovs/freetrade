import uuid
from collections import OrderedDict
from datetime import date

import requests
from dateutil import relativedelta, parser

from . import Auth


class API:
    def __init__(self, auth: Auth, host: str, useragent: str = None):
        self.auth = auth
        self.host = 'https://' + host
        self.useragent = useragent if useragent else 'Freetrade/1.0.4756-4756 Dalvik/2.1.0 ' \
                                                     '(Linux; U; Android 9; SM-G965U Build/PPR1.180610.011)'
        session_id = auth.headers['session_id']

        self.headers = OrderedDict([
            ('Authorization', self.auth.get_auth_bearer()),
            ('session_id', session_id),
            ('request_id', ''),
            ('User-Agent', self.useragent),
            ('Host', host),
            ('Connection', 'close'),
            ('Accept-Encoding', 'gzip, deflate')
        ])

    def get_request_header(self) -> OrderedDict:
        self.headers['request_id'] = str(uuid.uuid4())
        return self.headers

    def get_address_by_postcode(self, postcode: str) -> dict:
        self.auth.keep_id_token_valid()
        headers = self.get_request_header()

        response = requests.get(self.host + '/proxy/postcodelookup/uk/' + postcode, headers=headers)

        return response.json()

    def validate_bank(self, sort_code: str, account_number: str) -> dict:
        # sort code is a 6 digit string without hyphens
        self.auth.keep_id_token_valid()
        headers = self.get_request_header()
        url = f'{self.host}/proxy/bankvalidation/sortCode/{sort_code}/account/{account_number}'
        response = requests.get(url, headers=headers)

        return response.json()

    def withdraw_funds(self, account_id: str, amount: str) -> requests.Response:
        self.auth.keep_id_token_valid()

        url = self.host + '/banking/withdraw-funds'
        payload = {
            'account_id': account_id,
            'amount': amount  # e.g. '1.00'
        }
        res = requests.post(url, json=payload, headers=self.get_request_header())

        return res

    def set_active_account(self, client_id: str, account_id: str) -> requests.Response:
        self.auth.keep_id_token_valid()

        url = self.host + '/clients/{}/set-active-account'.format(client_id)
        payload = {
            'account_id': account_id
        }
        res = requests.post(url, json=payload, headers=self.get_request_header())

        return res

    def onboard_user(self, email: str, first_name: str, last_name: str, date_of_birth: date,
                     nationality: str, ni_number: str, number: str, premise: str, street: str,
                     post_town: str, county: str, postcode: str, country: str, account_type: str,
                     base_currency: str) -> requests.Response:
        self.auth.keep_id_token_valid()

        url = self.host + '/clients/client-onboard-requests'

        payload = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': date_of_birth.strftime('%Y-%m-%d'),  # YYYY-MM-DD
            'nationality': nationality,  # 3 letter code
            'id_numbers': {
                'NI_NUMBER': ni_number  # 9 symbol
            },
            'address': {
                'number': number,
                'premise': premise,
                'street': street,
                'posttown': post_town,
                'county': county,
                'postcode': postcode,
                'country': country  # 3 letter code
            },
            'account_type': account_type,  # GIA or ... ISA?
            'base_currency': base_currency
        }
        res = requests.post(url, json=payload, headers=self.get_request_header())

        return res

    def get_ticker_history_iextrading(self, ticker: str, duration: str = '1m') -> dict:
        # Does not support securities from LSE (London Stock Exchange)

        # FreeTrade uses API from IEX trading to get price history
        # https://iextrading.com/developer/docs/#chart
        # duration: 5y, 2y, 1y, ytd, 6m, 3m, 1m, 1d
        url = f'{self.host}/proxy/iex/v1/stock/{ticker}/chart/{duration}'

        response = requests.get(url, headers=self.get_request_header())

        return None if response.status_code != 200 else response.json()

    def get_ticker_history_quandl(self, ticker: str, ftexchange: str = 'XLON', start_date: date = None) -> dict:
        if start_date is None:
            start_date = date.today() - relativedelta.relativedelta(months=1)

        start_date_str = start_date.strftime('%Y-%m-%d')
        symbol = ticker.replace('.', '_')

        url = f'{self.host}/proxy/quandl/v3/datasets/{ftexchange}/{symbol}/data.json?' \
            f'column_index=4&order=asc&start_date={start_date_str}'

        response = requests.get(url, headers=self.get_request_header())

        return None if response.status_code != 200 else response.json()

    def get_ticker_history(self, ticker: str, ftexchange: str, duration: str = '1m') -> OrderedDict:
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

            history = self.get_ticker_history_quandl(ticker, ftexchange, history_date)

            data = OrderedDict((history_date, price)
                               for history_date, price in history['dataset_data']['data'])
        else:
            history = self.get_ticker_history_iextrading(ticker, duration)
            data = OrderedDict((price['date'], price['close'])
                               for price in history)

        return data
