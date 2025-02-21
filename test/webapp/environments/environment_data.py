import json
from pprint import pprint


class Environment:
    values = {}

    @classmethod
    def get_value(cls, key):
        return cls.values.get(key, False)

    @classmethod
    def parse_environment_file(cls, file_path):
        # We're going off of the postman environment file format, which looks like this:
        # {
        #     "values": [
        #         {
        #             "key": "var_name",
        #             "value": "val"
        #         }
        #     ]
        # }
        # It's a weird data structure, but postman environments are used often,
        # including in our API testing, so it makes sense to just adopt that format.
        with open(file_path, 'r') as file:
            data = json.load(file)
        for item in data['values']:
            cls.values[item['key']] = item['value']

    @classmethod
    def print_environment_info(cls):
        pprint(cls.values)

    @classmethod
    def fetch_env_vars(cls, key_list):
        env_dict = {}
        for key in key_list:
            value = cls.get_value(key)
            if not value:
                raise ValueError(f"Environment variable '{key}' is missing from the environment file.")
            env_dict[key] = value
        return env_dict
