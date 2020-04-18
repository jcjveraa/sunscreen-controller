import json
import os

def get_secrets() -> dict:
    fileDir = os.path.dirname(os.path.abspath(__file__))
    secrets_file = 'secrets.json'
    with open(os.path.join(fileDir, secrets_file)) as secrets_json:
        secrets = json.load(secrets_json)
    return secrets

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
