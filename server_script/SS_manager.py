import requests
import json
import os


class SunScreenManager():
    fileDir = os.path.dirname(os.path.abspath(__file__))
    secrets_file = 'secrets.json'

    def get_Open_Weather_JSON(self):
        """Gets the JSON response from openweathermap"""
        with open(os.path.join(self.fileDir, self.secrets_file)) as secrets_json:
            secrets = json.load(secrets_json)
            openWeatherAPIurl = "https://api.openweathermap.org/data/2.5/onecall?lat=" + \
                secrets['LAT'] + "&lon=" + secrets['LON'] + \
                "&appid=" + secrets['OPENWEATHERMAP_ORG_KEY']
            r = requests.get(openWeatherAPIurl)
            return r.json()

    def kelvin_to_celcius(self, tempKelvin: float) -> float:
        """Takes a temperature in degree Kelvin and returns the temperature in Celcius"""
        return tempKelvin - 273.15
