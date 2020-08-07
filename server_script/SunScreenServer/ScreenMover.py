import requests
from datetime import datetime

from .GetSecrets import append_json, write_json, get_secrets

def post_position_to_adafruit(position: int) -> int:
    secrets = get_secrets()
    try:
        adafruitFeed = secrets['ADAFRUIT_IO_FEEDS_URL'] + "sunscreenpos/data"
        headers = {'X-AIO-Key': secrets['ADAFRUIT_IO_KEY'], "Content-Type": "application/json"}
        payload = {'value':position}

        r = requests.post(adafruitFeed, json=payload, headers=headers)
        return 0
    except:
        print('Some exception occured in post_position_to_adafruit ...')
        return 999

def get_current_position() -> int:
    secrets = get_secrets()
    check_url = "http://{}/CurrentPosition?key={}"

    check_url = check_url.format(
        secrets["ESP_IP"],  secrets["ESP_KEY"])
    r = requests.get(check_url)
    try:
        json = r.json()
        position = int(json['position'])
        post_position_to_adafruit(position)
        return int(position )
    except:
        print('Some exception occured...')
        print(r.status_code)
        return 999

def move_sunscreen(percent_open: int):
    """Sends a command to the control unit - now via a Get request"""
    secrets = get_secrets()
    operate_url = "http://{}/Operate?targetPercentageOpen={}&key={}&timestamp={}"

    if get_current_position() is percent_open:
       print('not moving, current percentage already matches')
       exit()

    print("moving to " + str(percent_open))

    operate_url = operate_url.format(
        secrets["ESP_IP"], percent_open, secrets["ESP_KEY"], datetime.timestamp(datetime.now()))
    print(operate_url)
    r = requests.get(operate_url)
    try:
        print(r.status_code)
        print(r.json())
    except:
        print('Some exception occured...')
        pass
    print(r.status_code)
