from typing import Callable

from . import Credentials, Auth, API, Index, DataStore


class FreeTrade:
    def __init__(self, email: str = None, ft_key_file: str = None, otp_parser: Callable = None):
        # no key file given, look for one
        self.credentials = Credentials(ft_key_file)
        self.auth = None
        self.api = None
        self.index = Index(self.credentials)
        self.datastore = None

        if email is not None:
            self.auth = Auth(self.credentials, email, otp_parser=otp_parser)

            self.api = API(self.auth, self.credentials.get_ft_api_host())

            self.datastore = DataStore(self.api, self.index)
