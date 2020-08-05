# This runs as a standalone script (every minute) and as part of the module (every 20 minutes)

import requests
import json
from .GetSecrets import append_json, write_json, get_secrets
from SunScreenServer.ScreenMover import move_sunscreen

secrets = get_secrets()

def check_array_high_wind(wind_speed_arr):
    print('Wind speeds:', wind_speed_arr)
    return wind_speed_arr[3] >= secrets['HIGH_WIND_DIRECT_MEASUREMENT']

def get_data():
    windMosUrl = "http://"+secrets['WINDMOSIP']+"/counter"
    r = requests.get(windMosUrl)
    return r.json()

def screen_should_close():
    json_buffer = get_data()
    return check_array_high_wind(json_buffer['averages'])

def post_to_adafruit():
    json_buffer = get_data()
    adafruitFeed = secrets['ADAFRUIT_IO_FEEDS_URL'] + "wind/data"
    headers = {'X-AIO-Key': secrets['ADAFRUIT_IO_KEY'], "Content-Type": "application/json"}
    payload = {'value':json_buffer['averages'][3] }

    r = requests.post(adafruitFeed, json=payload, headers=headers)

# print(r.text)
