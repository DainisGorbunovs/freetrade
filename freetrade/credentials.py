import json
import os


class Credentials:
    def __init__(self, ft_key_file: str):
        if ft_key_file is None:
            # default local user configs
            key_paths_list = [
                'ft-keys.json',
                os.path.expanduser("~") + '/.config/freetrade/ft-keys.json'
            ]

            tmp_key_list = key_paths_list.copy()
            while not os.path.isfile(key_paths_list[0]):
                tmp_key_list.pop(0)
                if not tmp_key_list:
                    raise OSError("No key file found at {}".format(key_paths_list))
            ft_key_file = tmp_key_list[0]

        with open(ft_key_file) as f:
            self.API_KEYS = json.load(f)

    def get_ft_auth_host(self):
        return self.API_KEYS['prod_auth_dealstream_host']

    def get_ft_api_host(self):
        return self.API_KEYS['prod_dealstream_host']

    def get_android_verification_api_key(self):
        return self.API_KEYS['google_android_device_verification_api_key']

    def get_algolia_api_key(self):
        return self.API_KEYS['algolia_api_key']

    def get_algolia_application_id(self):
        return self.API_KEYS['algolia_application_id']
