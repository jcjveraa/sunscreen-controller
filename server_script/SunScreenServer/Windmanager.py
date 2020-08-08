# This runs as a standalone script (every minute) and as part of the module (every 20 minutes)

import requests
import json
from .GetSecrets import append_json, write_json, get_secrets
from SunScreenServer.ScreenMover import move_sunscreen
from datetime import datetime,timedelta

secrets = get_secrets()

def check_array_high_wind(wind_speed_arr):
    if(secrets['LOGGING']):
        print('Wind speeds:', wind_speed_arr)
    return wind_speed_arr[3] >= secrets['HIGH_WIND_DIRECT_MEASUREMENT']

def get_data():
    windMosUrl = "http://"+secrets['WINDMOSIP']+"/counter"
    r = requests.get(windMosUrl)
    return r.json()

def screen_should_close():
    try:
        json_buffer = get_data()
        result = check_array_high_wind(json_buffer['averages']) or check_last_25_minutes_had_high_winds()
        return check_array_high_wind(json_buffer['averages'])
    except:
        return True


def post_to_adafruit():
    json_buffer = get_data()
    adafruitFeed = secrets['ADAFRUIT_IO_FEEDS_URL'] + "wind/data"
    headers = {'X-AIO-Key': secrets['ADAFRUIT_IO_KEY'], "Content-Type": "application/json"}
    payload = {'value':json_buffer['averages'][3] }

    r = requests.post(adafruitFeed, json=payload, headers=headers)

def check_last_25_minutes_had_high_winds(test_json_string=False):
    if test_json_string:
        print(test_json_string)
        json_buff = json.loads(test_json_string)
    else:
        start_time = (datetime.utcnow() - timedelta(minutes=25)).isoformat()
        adafruitFeed = secrets['ADAFRUIT_IO_FEEDS_URL'] + "wind/data?start_time=" + start_time
        headers = {'X-AIO-Key': secrets['ADAFRUIT_IO_KEY']}

        r = requests.get(adafruitFeed, headers=headers)
        json_buff = r.json()

    if(secrets['LOGGING']):
        print('Adafruit loaded!')
        print(json_buff)
    wind_check = any(float(x['value']) >= secrets['HIGH_WIND_DIRECT_MEASUREMENT'] for x in json_buff)
    if(secrets['LOGGING']):
        print('Wind check result')
        print(wind_check)
    return wind_check

# print(r.text)
