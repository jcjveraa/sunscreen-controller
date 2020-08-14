import requests

import numpy as np
import pandas as pd
import pvlib
from pvlib.pvsystem import PVSystem
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from datetime import datetime

from SunScreenServer.adafruitPoster import post_to_adafruit
from .GetSecrets import get_secrets


def theoretical_solar_output(temp_air=20):
    # For this example, we will be using Golden, Colorado
    secrets = get_secrets()
    tz = 'Europe/Amsterdam'
    lat, lon = secrets['LAT'], secrets['LON']

    # Create location object to store lat, lon, timezone
    site = Location(lat, lon, tz=tz)

    cec_modules = pvlib.pvsystem.retrieve_sam(name='CECMod')
    cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')

    lg_panels = cec_modules['LG_Electronics_Inc__LG325N1K_A5']
    solaredge_inverter = cec_inverters['SolarEdge_Technologies_Ltd___SE4000__240V_']
    surf_tilt = 20

    temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    location = site
    system = PVSystem(module_parameters=lg_panels,
                      inverter_parameters=solaredge_inverter,
                      surface_tilt=surf_tilt,
                      surface_azimuth=secrets['HOUSE_FACING_DEG'],
                      strings_per_inverter=12,
                      temperature_model_parameters=temperature_model_parameters)

    mc = ModelChain(system, location,  orientation_strategy="None",
                    aoi_model="physical", spectral_model="no_loss")

    daterange_now = pd.date_range(
        start=datetime.now(), periods=1, freq='1min', tz=tz)

    cs = site.get_clearsky(daterange_now)
    cs.insert(3, "temp_air", temp_air)
    mc.run_model(cs)
    return mc.ac.item()


def get_power(temperature=30):
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
    if (get_power() == 0 or theoretical_solar_output(temperature) == 0):
        return True
    if(get_power() > (0.25*theoretical_solar_output(temperature))):
        return False
    else:
        return True
