from datetime import datetime
import requests
import redis

from SunScreenServer.adafruitPoster import post_to_adafruit

from .GetSecrets import get_secrets


def theoretical_solar_output(temp_air=20):
    r = redis.Redis(db = 1)
    temp_air = round(temp_air)
    key = datetime.now().replace(microsecond=0, second=0).astimezone(
    ).isoformat() + '_temp=' + str(temp_air)
    cache_result = r.get("key")

    if cache_result:
        return cache_result
    else:
        generate_theoretical_solar_output(temp_air)
        return theoretical_solar_output(temp_air)


def generate_theoretical_solar_output(temp_air=20):
    import numpy as np
    import pandas as pd
    import pvlib
    from pvlib.pvsystem import PVSystem
    from pvlib.location import Location
    from pvlib.modelchain import ModelChain
    from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
    # For this example, we will be using Golden, Colorado
    secrets = get_secrets()
    tz = 'Europe/Amsterdam'
    lat, lon = float(secrets['LAT']), float(secrets['LON'])

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

    # select the DB and flush it first
    r = redis.Redis(db = 1)
    r.flushdb()
    print("Current theoretical solar cache size after flushing:", r.dbsize())
    print(range(temp_air-10, temp_air+10))

    for temp in range(temp_air-10, temp_air+10):
        weather = cs.copy()
        weather.insert(3, "temp_air", temp)
        mc.run_model(weather)
        print(mc.ac)

        for index, ac_power in mc.ac.items():
            redis_key = index.to_pydatetime().replace(
                microsecond=0, second=0).astimezone().isoformat() + '_temp=' + str(temp_air)
            r.set(redis_key, ac_power)
            name = input(redis_key + str(ac_power))
    print("Current theoretical solar cache size after filling:", r.dbsize())


def get_power():
    try:
        import time
        r = redis.Redis(db = 0)
        secrets = get_secrets()

        siteId = secrets['SOLAREDGE_SITEID']
        sApiKey = secrets['SOLAREDGE_KEY']
        solar_edge_url = f"https://monitoringapi.solaredge.com/site/{siteId}/overview?api_key={sApiKey}&format=json"
        # print(solar_edge_url)

        overview = requests.get(solar_edge_url).json()
        # print(overview)
        currentPower = overview['overview']['currentPower']['power']
        current_energy_watthour = overview['overview']['lifeTimeData']['energy']

        previous_energy_watthour = float(r.get('previous_energy_watthour'))
        previous_energy_watthour_timestamp = float(r.get(
            'previous_energy_watthour_timestamp'))

        now_timestamp = time.time()

        # convert watthour + time interval in seconds to power
        if previous_energy_watthour and previous_energy_watthour_timestamp:
            hours_passed = (
                now_timestamp - previous_energy_watthour_timestamp)/3600
            currentPower = (currentEnergy - previousEnergy) / hours_passed

        r.set('previous_energy_watthour', current_energy_watthour)
        r.set('previous_energy_watthour_timestamp', now_timestamp)

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
