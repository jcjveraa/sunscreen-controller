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

def is_cloudy(weather: dict):
    """Returns true if its nighttime in this particular slot"""
    if(all(x in weather for x in ['clouds'])):
        return weather['clouds'] > 50
    else:
        raise Exception(
            'No cloudiness info found in forecast!'
        )

def should_sunscreen_open(LOW_TEMP: float, HIGH_WIND: float) -> bool:
    try:
        onecall = get_Open_Weather_JSON()
        is_current(onecall)
        next_fcst = get_next_forecast(onecall)
        current = onecall['current']

        checks = list()

        # Check the current weather
        checks.append(has_low_temp(current, LOW_TEMP))
        checks.append(is_nighttime(current))
        checks.append(has_rain(current))
        checks.append(has_high_winds(current, HIGH_WIND))
        checks.append(is_cloudy(current))

        # Check the forecast
        checks.append(has_rain(next_fcst))
        checks.append(has_high_winds(next_fcst, HIGH_WIND))

        return not any(checks)

    except Exception as e:
        raise Exception(e)
