from datetime import datetime
import requests
import redis

from SunScreenServer.adafruitPoster import post_to_adafruit

from .GetSecrets import get_secrets


def theoretical_solar_output(temp_air=20):
    # force temp to int - close enough...
    temp_air = int(temp_air)
    r = redis.Redis(db=1)
    temp_air = round(temp_air)
    key = round_time(datetime.now(), 10*60).replace(microsecond=0, second=0).astimezone(
    ).isoformat() + '_temp=' + str(temp_air)
    cache_result = r.get(key)

    if cache_result:
        print('Cached result loaded for key:', key)
        return float(cache_result)
    else:
        print('No cached result for key', key,
              ', populating Redis database number 1...')
        generate_theoretical_solar_output(temp_air)
        return theoretical_solar_output(temp_air)


def round_time(dt, round_to_seconds=60):
    """Round a datetime object to any number of seconds
    dt: datetime.datetime object
    round_to_seconds: closest number of seconds for rounding, Default 1 minute.
    """
    rounded_epoch = round(dt.timestamp() / round_to_seconds) * round_to_seconds
    rounded_dt = datetime.fromtimestamp(rounded_epoch).astimezone(dt.tzinfo)
    return rounded_dt


def generate_theoretical_solar_output(temp_air=20):
    from datetime import timedelta
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

    # daterange_now = pd.date_range(
    #     start=datetime.now().replace(
    #             microsecond=0, second=0), periods=1, freq='1min', tz=tz)
    start_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1, minutes=-1)

    daterange_now = pd.date_range(
        start=start_date, end=end_date, freq='10min', tz=tz)
    cs = site.get_clearsky(daterange_now)

    # select the DB and flush it first
    r = redis.Redis(db=1)
    r.flushdb()
    print("Current theoretical solar cache size after flushing:", r.dbsize())
    # print(range(temp_air-10, temp_air+10))

    for temp in range(temp_air-10, temp_air+10):
        weather = cs.copy()
        weather.insert(3, "temp_air", temp)
        mc.run_model(weather)
        # print(mc.ac)

        for index, ac_power in mc.ac.items():
            redis_key = index.to_pydatetime().replace(
                microsecond=0, second=0).astimezone().isoformat() + '_temp=' + str(temp)
            r.set(redis_key, ac_power)
            # name = input(redis_key + str(ac_power))
    print("Current theoretical solar cache size after filling:", r.dbsize())


def get_power():
    try:
        import time
        r = redis.Redis(db=0)
        secrets = get_secrets()

        siteId = secrets['SOLAREDGE_SITEID']
        sApiKey = secrets['SOLAREDGE_KEY']
        solar_edge_url = f"https://monitoringapi.solaredge.com/site/{siteId}/overview?api_key={sApiKey}&format=json"
        # print(solar_edge_url)

        overview = requests.get(solar_edge_url).json()
        # print(overview)
        currentPower = overview['overview']['currentPower']['power']
        current_energy_watthour = overview['overview']['lifeTimeData']['energy']

        now_timestamp = time.time()

        previous_energy_watthour = r.get('previous_energy_watthour')
        previous_energy_watthour_timestamp = r.get(
            'previous_energy_watthour_timestamp')

        # convert watthour + time interval in seconds to power
        if previous_energy_watthour and previous_energy_watthour_timestamp:
            previous_energy_watthour_timestamp = float(
                previous_energy_watthour_timestamp)
            hours_passed = (
                now_timestamp - previous_energy_watthour_timestamp)/3600
            currentPower = (current_energy_watthour - float(previous_energy_watthour)) / hours_passed

        r.set('previous_energy_watthour', current_energy_watthour)
        r.set('previous_energy_watthour_timestamp', now_timestamp)

        print('power is',currentPower)

        post_to_adafruit("solar", currentPower)
        return currentPower
    except:
        return -1


def screen_should_close(temperature=30):
    secrets = get_secrets()
    curr_power = get_power()
    theo_power = theoretical_solar_output(temperature)
    print('current & theo:',curr_power, theo_power)
    if (curr_power <= secrets['SOLAR_POWER_LIMIT'] or theo_power <= 0):
        return True
    if(curr_power > (0.25*theo_power)):
        return False
    else:
        return True
