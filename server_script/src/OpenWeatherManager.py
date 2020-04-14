import requests
import json
import os
import time


class OpenWeatherManager():

    json_buffer = dict()

    def get_Open_Weather_JSON(self, typeString="onecall"):
        """Gets the JSON response from openweathermap. Types are forecast, weather, onecall. Defauls to onecall."""
        fileDir = os.path.dirname(os.path.abspath(__file__))
        secrets_file = 'secrets.json'
        with open(os.path.join(fileDir, secrets_file)) as secrets_json:
            secrets = json.load(secrets_json)
            openWeatherAPIurl = "https://api.openweathermap.org/data/2.5/"+typeString+"?lat=" + \
                secrets['LAT'] + "&lon=" + secrets['LON'] + \
                "&appid=" + secrets['OPENWEATHERMAP_ORG_KEY']
            r = requests.get(openWeatherAPIurl)
            self.json_buffer[typeString] = r.json()
            return self.json_buffer[typeString]

    def kelvin_to_celcius(self, tempKelvin: float) -> float:
        """Takes a temperature in degree Kelvin and returns the temperature in Celcius"""
        return tempKelvin - 273.15

    def oncecall_is_current(self, allowed_delta=(5*60)):
        """Returns true if the json object current.dt timestamp is within allowed delta of now"""
        if (self.json_buffer['onecall']):
            return self.time_is_current(self.json_buffer['onecall']['current']['dt'], allowed_delta)
        else:
            return False

    def time_is_current(self, time_to_check, allowed_delta=(5*60)):
        """Returns true if the json object current.dt timestamp is within allowed delta of now"""
        current_time = time.time()
        if (time_to_check):
            return time_to_check <= (current_time + allowed_delta)
        else:
            return False

    def refresh_if_required(self):
        if(not self.oncecall_is_current):
            self.get_Open_Weather_JSON()
        if(not self.oncecall_is_current):
            raise Exception('API not refreshing properly')

    def get_next_forecast(self, allowed_delta=(3*60*60)):
        """Gets the next forecast which is less than 3 hours away"""
        self.refresh_if_required()
        x = self.json_buffer['onecall']['hourly']
        sorted_forecast = sorted(x.items(), key=lambda item: item['dt'])
        next_forecast = sorted_forecast[0]
        if(self.time_is_current(next_forecast['dt'], allowed_delta)):
            return next_forecast
        else:
            raise Exception('get_next_forecast time not within 3 hours, apparently')

    def get_current(self):
        """Gets the next forecast which is less than 3 hours away"""
        self.refresh_if_required()
        x = self.json_buffer['onecall']['hourly']
        sorted_forecast = sorted(x.items(), key=lambda item: item['dt'])
        next_forecast = sorted_forecast[0]
        return next_forecast

    # def get
