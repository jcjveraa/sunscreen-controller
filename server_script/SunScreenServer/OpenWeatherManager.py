import requests
import json
import os
import time


def get_Open_Weather_JSON(typeString="onecall"):
    """Gets the JSON response from openweathermap. Types are forecast, weather, onecall. Defauls to onecall."""
    fileDir = os.path.dirname(os.path.abspath(__file__))
    secrets_file = 'secrets.json'
    with open(os.path.join(fileDir, secrets_file)) as secrets_json:
        secrets = json.load(secrets_json)
        openWeatherAPIurl = "https://api.openweathermap.org/data/2.5/"+typeString+"?lat=" + \
            secrets['LAT'] + "&lon=" + secrets['LON'] + \
            "&appid=" + secrets['OPENWEATHERMAP_ORG_KEY']
        r = requests.get(openWeatherAPIurl)
        json_buffer = r.json()
        return json_buffer


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
        return False


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


def forecast_has_rain(hourly_forecast: dict) -> bool:
    return 'rain' in hourly_forecast.keys()


def forecast_has_high_winds(hourly_forecast: dict, max_wind: float):
    if('wind_speed' in hourly_forecast.keys()):
        return hourly_forecast['wind_speed'] >= max_wind
    else:
        raise Exception(
            'No wind found in forecast!'
        )
