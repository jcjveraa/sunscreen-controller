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
