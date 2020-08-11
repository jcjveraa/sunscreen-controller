from SunScreenServer.GetSecrets import get_secrets
import requests


def post_to_adafruit(feed, value):
    try:
        secrets = get_secrets()
        adafruitFeed = secrets['ADAFRUIT_IO_FEEDS_URL'] + f"{feed}/data"
        headers = {'X-AIO-Key': secrets['ADAFRUIT_IO_KEY'], "Content-Type": "application/json"}
        payload = {'value':value }

        r = requests.post(adafruitFeed, json=payload, headers=headers)

    except :
        pass
