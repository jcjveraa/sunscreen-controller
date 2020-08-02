import json
import os
from functools import lru_cache

@lru_cache(maxsize=10)
def get_secrets() -> dict:
    fileDir = os.path.dirname(os.path.abspath(__file__))

    result = {}

    secrets_file = 'secrets.json'
    config_file = 'config.json'
    try:
        with open(os.path.join(fileDir, secrets_file)) as secrets_json:
            secrets = json.load(secrets_json)
            result.update(secrets)
    except:
        print('secrets.json not available, perhaps in testing mode?')
    with open(os.path.join(fileDir, config_file)) as config_json:
        config = json.load(config_json)
        result.update(config)
    return result

def write_json(json_buffer: dict, location: str):
    fileDir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(fileDir, location), mode='w') as file:
            json.dump(json_buffer, file)

def append_json(location: str, dict_to_append: dict):
    fileDir = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(fileDir, location)) as file:
            data = json.load(file)
            data['logs'].append(dict_to_append)
        write_json(data, location)
    except:
        data = dict()
        data['logs'] = list()
        data['logs'].append(dict_to_append)
        write_json(data, location)
