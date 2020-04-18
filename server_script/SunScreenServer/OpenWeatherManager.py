import requests
import json
import os
import time
from SunScreenServer.GetSecrets import get_secrets, write_json


def get_Open_Weather_JSON(typeString="onecall"):
    """Gets the JSON response from openweathermap. Types are forecast, weather, onecall. Defauls to onecall."""
    secrets = get_secrets()
    openWeatherAPIurl = "https://api.openweathermap.org/data/2.5/"+typeString+"?lat=" + \
        secrets['LAT'] + "&lon=" + secrets['LON'] + \
        "&appid=" + secrets['OPENWEATHERMAP_ORG_KEY']
    r = requests.get(openWeatherAPIurl)
    json_buffer = r.json()
    write_json(json_buffer, 'most_recent.json')
    if(is_current(json_buffer)):
        return json_buffer
    else:
        raise Exception(
            'JSON data was not current in get_Open_Weather_JSON'
        )


def get_solar_noon(current_weather: dict) -> float:
    """Returns the time of solar noon, directly 'in between' sunrise and sunset"""
    if(all(x in current_weather for x in ['sunrise', 'sunset'])):
        return ((current_weather['sunset']-current_weather['sunrise'])/2 + current_weather['sunrise'])
    else:
        raise Exception(
            'No sunrise/sunset info found in forecast for get_solar_noon!'
        )


def kelvin_to_celcius(tempKelvin: float) -> float:
    """Takes a temperature in degree Kelvin and returns the temperature in Celcius"""
    return tempKelvin - 273.15


def is_current(json_buffer_onecall, allowed_delta=(5*60),):
    """Returns true if the json object current.dt timestamp is within allowed delta of now"""
    if (json_buffer_onecall):
        return (time_is_current(json_buffer_onecall['current']['dt'], allowed_delta))
    else:
        return False


def time_is_current(time_to_check, allowed_delta=(5*60)):
    """Returns true if the json object current.dt timestamp is within allowed delta of now"""
    current_time = time.time()
    if (time_to_check):
        return time_to_check <= (current_time + allowed_delta)
    else:
        raise Exception(
            'This was an outdated forecast')


def get_next_forecast(json_buffer, allowed_delta=(3*60*60)):
    """Gets the next forecast which is less than 3 hours away"""
    x = json_buffer['hourly']
    # sorted_forecast = sorted(x.items(), key=lambda item: item['dt'])
    next_forecast = x[0]
    if(time_is_current(next_forecast['dt'], allowed_delta)):
        return next_forecast
    else:
        raise Exception(
            'get_next_forecast time not within 3 hours, apparently')


def has_rain(weather: dict) -> bool:
    """Returns True if the Rain keyword is there"""
    return 'rain' in weather.keys()


def has_high_winds(weather: dict, max_wind: float):
    wind_gust = False
    if('wind_gust' in weather.keys()):
        wind_gust = weather['wind_gust'] >= max_wind

    if('wind_speed' in weather.keys()):
        wind_speed = weather['wind_speed'] >= max_wind
        return wind_gust or wind_speed
    else:
        raise Exception(
            'No wind found in forecast!'
        )


def has_low_temp(weather: dict, min_temp_celcius: float):
    if('temp' in weather.keys()):
        return kelvin_to_celcius(weather['temp']) <= min_temp_celcius
    else:
        raise Exception(
            'No temp found in forecast!'
        )


def is_nighttime(weather: dict):
    """Returns true if its nighttime in this particular slot"""
    if(all(x in weather for x in ['sunrise', 'sunset'])):
        now = weather['dt']
        return now < weather['sunrise'] or now > weather['sunset']
    else:
        raise Exception(
            'No sunrise/sunset info found in forecast!'
        )


def is_cloudy(weather: dict, cloud_limit=50):
    """Returns true if its nighttime in this particular slot"""
    if(all(x in weather for x in ['clouds'])):
        return weather['clouds'] > cloud_limit
    else:
        raise Exception(
            'No cloudiness info found in forecast!'
        )


def check_list(onecall: dict = None) -> dict:
    try:
        secrets = get_secrets()
        LOW_TEMP = secrets['LOW_TEMP']
        HIGH_WIND = secrets['HIGH_WIND']
        if onecall is None:
            onecall = get_Open_Weather_JSON()
        is_current(onecall)
        next_fcst = get_next_forecast(onecall)
        current = onecall['current']

        checks = dict()

        # Check the current weather
        checks['current_has_low_temp'] = has_low_temp(current, LOW_TEMP)
        checks['current_has_rain'] = has_rain(current)
        checks['current_has_high_winds'] = has_high_winds(current, HIGH_WIND)
        checks['current_is_cloudy'] = is_cloudy(current, secrets['CLOUDS'])
        # Check the forecast
        checks['fcst_has_rain'] = has_rain(next_fcst)
        checks['fcst_has_high_winds'] = has_high_winds(next_fcst, HIGH_WIND)

        return checks

    except Exception as e:
        raise Exception(e)


def should_sunscreen_open(onecall: dict = None) -> bool:
    return not any(check_list(onecall).values())
