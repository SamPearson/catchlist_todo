import json

values = {}


def get_value(key):
    if key in values:
        return values[key]
    else:
        return False


def parse_environment_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    # We're going off of the postman environment file format, which looks like this:
    # {
    #     "values": [
    #         {
    #             "key": "var_name",
    #             "value": "val"
    #         }
    #     ]
    # }
    # It's a weird data structure, but postman environments are used in a lot of places,
    # So it makes sense to just adopt that format.

    # Extract key-value pairs from the 'values' list and update globals
    for item in data['values']:
        key = item['key']
        value = item['value']
        globals()['values'][key] = value


def print_environment_info():
    from pprint import pprint
    pprint(values)


def fetch_env_vars(key_list):
    # This method fetches a subset of the data in the available environment file.
    # It also throws an exception if that data is not present.
    # use it at the beginning of each test to confirm you have the data you need,
    # and if you don't, fail the test immediately with a clear message.
    env_dict = {}
    for key in key_list:
        assert get_value(key), f"Cannot continue, the env var {key} is not set."
        env_dict[key] = get_value(key)

    return env_dict


