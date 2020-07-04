# For now this is a standalone script
import requests
import json
from GetSecrets import get_secrets, write_json

secrets = get_secrets()
windMosUrl = "http://"+secrets['WINDMOSIP']+"/counter"
r = requests.get(windMosUrl)
json_buffer = r.json()
# print(json_buffer)

adafruitFeed = secrets['ADAFRUIT_IO_FEEDS_URL'] + "wind/data"

headers = {'X-AIO-Key': secrets['ADAFRUIT_IO_KEY'], "Content-Type": "application/json"}
payload = {'value':json_buffer['averages'][3] }

r = requests.post(adafruitFeed, json=payload, headers=headers)
# print(r.text)
