import os
import uuid
from collections import OrderedDict
from requests import Session
from typing import Callable
import json
import logging
import jwt
from datetime import datetime

logger = logging.getLogger(__name__)


class Auth:
    def __init__(self, host: str, android_api_key: str, email: str, useragent: str = None, session_id: str = None):
        self.custom_token = None
        self.id_token = None
        self.refresh_token = None

        self.host = 'https://' + host
        self.email = email
        self.useragent = useragent if useragent else 'Freetrade/1.0.3701-3701 Dalvik/2.1.0' \
                                                     ' (Linux; U; Android 9; GT-I9300 Build/PQ2A.190405.003)'
        self.android_api_key = android_api_key

        if session_id is None:
            session_id = str(uuid.uuid4())

        self.headers = OrderedDict([
            ('session_id', session_id),
            ('request_id', ''),
            ('User-Agent', self.useragent),
            ('Content-Type', 'application/x-www-form-urlencoded'),
            ('Content-Length', ''),
            ('Host', host),
            ('Connection', 'close'),
            ('Accept-Encoding', 'gzip, deflate')
        ])

    def get_request_header(self):
        self.headers['request_id'] = str(uuid.uuid4())
        return self.headers

    def login_request_otp(self):
        session = Session()
        session.headers = self.get_request_header()

        payload = {'email': self.email}
        response = session.post(self.host + '/start', data=payload)

        return response

    def login_with_otp(self, one_time_password: str):
        session = Session()
        session.headers = self.get_request_header()

        payload = {'email': self.email, 'otp': one_time_password}
        response = session.post(self.host + '/login', data=payload)

        content = response.json()
        self.custom_token = content['access_token']

        return response

    def authenticate(self, session_file: str = None, otp_parser: Callable = None):
        if otp_parser is None:
            otp_parser = lambda: input('What is the OTP (one time password) in the Magic link in the email? ')

        # default local user configs
        key_paths_list = [
            'ft-session.json',
            os.path.expanduser("~") + '/.config/freetrade/ft-session.json',
        ]

        # if session_file is given, prioritise by reading from it first
        if session_file is not None:
            key_paths_list.insert(0, session_file)

        # check which files are readable and contain the session
        session = None
        for path in key_paths_list:
            # if there are issues reading file, ignore them
            # and just relogin again
            try:
                if os.path.isfile(path):
                    with open(path, 'rb') as f:
                        session = json.load(f)
                        self.refresh_token = session['refresh_token']
                        self.headers['session_id'] = session['session_id']
                        self.refresh_id_token()
                        break
            except Exception as e:
                logger.error('Error reading session file: {} - {}.'.format(type(e).__name__, str(e)))
                session = None

        # if none of the files were successful, login again
        if session is None:
            self.login_request_otp()
            otp = otp_parser()
            # get a Custom Token for authenticating Firebase client SDKs
            # valid for 1 hour
            self.login_with_otp(otp)

            # get a refresh token (valid 1 year) and ID token (valid 1 hour)
            self.get_firebase_tokens()

            # save the new session
            with open(key_paths_list[0], 'w') as f:
                data = {
                    'refresh_token': self.refresh_token,
                    'session_id': self.headers['session_id']
                }
                json.dump(data, f)

    def get_firebase_tokens(self):
        # if does not work, need new session token (relogin via authenticate)
        # exchange custom token -> a refresh and ID tokens

        # https://firebase.google.com/docs/reference/rest/auth
        session = Session()
        url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken?key='\
              + self.android_api_key
        res = session.post(url, json={
            'token': self.custom_token,
            'returnSecureToken': True
        })

        tokens = res.json()
        self.refresh_token = tokens['refreshToken']
        self.id_token = tokens['idToken']

    def refresh_id_token(self):
        # exchange refresh token -> newer refresh and ID token

        session = Session()
        url = 'https://securetoken.googleapis.com/v1/token?key=' + self.android_api_key
        res = session.post(url, data={
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        })

        tokens = res.json()
        self.refresh_token = tokens['refresh_token']
        self.id_token = tokens['id_token']

        self.headers['Authorization'] = self.get_auth_bearer()
        self.headers.move_to_end('Authorization', last=False)

    def get_auth_bearer(self):
        return 'Bearer ' + self.id_token

    def keep_id_token_valid(self):
        decoded = jwt.decode(self.id_token, verify=False)
        delta_time_valid = datetime.utcfromtimestamp(decoded['exp']) - datetime.utcnow()

        # if less than 60 seconds left, refresh ID token
        if delta_time_valid.total_seconds() < 60:
            self.refresh_id_token()

    def onboard_user(self, email: str, first_name: str, last_name: str, date_of_birth: str,
                         nationality: str, ni_number: str, number: str, premise: str, street: str,
                         post_town: str, county: str, postcode: str, country: str, account_type: str,
                         base_currency: str):
        self.keep_id_token_valid()

        session = Session()
        url = self.host + '/clients/client-onboard-requests'

        payload = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': date_of_birth,  # YYYY-MM-DD
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
        res = session.post(url, json=payload)

        return res

