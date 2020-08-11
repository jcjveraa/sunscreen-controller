from datetime import datetime

import requests
from numpy import array, cos, deg2rad, sin
from solarpy import solar_panel

from SunScreenServer.adafruitPoster import post_to_adafruit

from .GetSecrets import get_secrets


def theoretical_solar_output(temperature = 30):
    secrets = get_secrets()
    s = 1.686 * 1.016 * 12  # m2
    eff = 0.190 - 0.0037*(temperature-25)

    alpha = deg2rad(270+180 - 226.38)
    beta = deg2rad(30)

    x = cos(alpha) * cos(beta)
    z = sin(alpha) * cos(beta)
    y = sin(beta)

    sp5 = solar_panel(s, eff, 'panels')
    sp5.set_orientation(array([z, x, -y]))

    lat, lng, h = float(secrets['LAT']), float(secrets['LON']), 0

    sp5.set_position(lat, lng, h)
    sp5.set_datetime(datetime.now())
    # print(sp5.power())
    return sp5.power()

def get_power(temperature = 30):
    try:
        secrets = get_secrets()
        siteId = secrets['SOLAREDGE_SITEID']
        sApiKey = secrets['SOLAREDGE_KEY']
        solar_edge_url = f"https://monitoringapi.solaredge.com/site/{siteId}/overview?api_key={sApiKey}"
        # print(solar_edge_url)

        overview = requests.get(solar_edge_url).json()
        # print(overview)
        currentPower = overview['overview']['currentPower']['power']
        post_to_adafruit("solar", currentPower)
        return currentPower
    except:
        return -1


def screen_should_close(temperature=30):
    if(get_power() > (0.25*theoretical_solar_output(temperature))):
        return False
    else:
        return True


theoretical_solar_output()
