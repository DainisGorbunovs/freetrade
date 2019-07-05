import uuid
from collections import OrderedDict

from requests import Session

from . import Auth


class API:
    def __init__(self, auth: Auth, host: str, useragent: str = None):
        self.auth = auth
        self.host = 'https://' + host
        self.useragent = useragent if useragent else 'Freetrade/1.0.4435-4435 Dalvik/2.1.0 ' \
                                                     '(Linux; U; Android 9; SM-G965U Build/PPR1.180610.011)'
        session_id = auth.headers['session_id']

        self.headers = OrderedDict([
            ('Authorization', self.auth.get_auth_bearer()),
            ('session_id', session_id),
            ('request_id', ''),
            ('User-Agent', self.useragent),
            # ('Content-Type', 'application/x-www-form-urlencoded'),
            # ('Content-Length', ''),
            ('Host', host),
            ('Connection', 'close'),
            ('Accept-Encoding', 'gzip, deflate')
        ])

    def get_request_header(self):
        self.headers['request_id'] = str(uuid.uuid4())
        return self.headers

    def get_address_by_postcode(self, postcode: str):
        self.auth.keep_id_token_valid()

        session = Session()
        session.headers = self.get_request_header()

        response = session.get(self.host + '/proxy/postcodelookup/uk/' + postcode)

        return response.json()

    def withdraw_funds(self, account_id: str, amount: str):
        self.auth.keep_id_token_valid()

        session = Session()
        session.headers = self.get_request_header()

        url = self.host + '/banking/withdraw-funds'
        payload = {
            'account_id': account_id,
            'amount': amount  # e.g. '1.00'
        }
        res = session.post(url, json=payload)

        return res

    def set_active_account(self, client_id: str, account_id: str):
        self.auth.keep_id_token_valid()

        session = Session()
        session.headers = self.get_request_header()

        url = self.host + '/clients/{}/set-active-account'.format(client_id)
        payload = {
            'account_id': account_id
        }
        res = session.post(url, json=payload)

        return res
