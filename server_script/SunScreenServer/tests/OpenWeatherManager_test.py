import unittest
import OpenWeatherManager
import json
import os
import time
fileDir = os.path.dirname(os.path.abspath(__file__))


class OWMTest(unittest.TestCase):

    def test_Kelvin_to_Celcius(self):
        self.assertEqual(OpenWeatherManager.kelvin_to_celcius(0), -273.15)
        self.assertNotEqual(OpenWeatherManager.kelvin_to_celcius(1), -270.15)

    def test_is_current_check(self):
        OWjson = json.load(open(os.path.join(fileDir, 'onecall.json')))
        OWjson['current']['dt'] = time.time()
        self.assertTrue(OpenWeatherManager.is_current(OWjson))
        self.assertFalse(OpenWeatherManager.is_current(OWjson, -(5*60)))

    def test_sunset_sunrise(self):
        OWjson = json.load(open(os.path.join(fileDir, 'onecall.json')))
        self.assertFalse(OpenWeatherManager.is_nighttime(OWjson['current']))
        OWjson['current']['dt'] = OWjson['current']['sunrise']-1
        self.assertTrue(OpenWeatherManager.is_nighttime(OWjson['current']))
        OWjson['current']['dt'] = OWjson['current']['sunset']+1
        self.assertTrue(OpenWeatherManager.is_nighttime(OWjson['current']))

    def test_next_forecast(self):
        OWjson = json.load(open(os.path.join(fileDir, 'onecall.json')))
        self.assertTrue('dt' in OpenWeatherManager.get_next_forecast(OWjson))

    def test_high_winds(self):
        OWjson = json.load(open(os.path.join(fileDir, 'onecall.json')))
        self.assertFalse(OpenWeatherManager.has_high_winds(
            OWjson['hourly'][0], 3.4))
        self.assertTrue(OpenWeatherManager.has_high_winds(
            OWjson['hourly'][1], 3.4))

    def test_rain(self):
        OWjson = json.load(open(os.path.join(fileDir, 'onecall.json')))
        self.assertFalse(OpenWeatherManager.has_rain(
            OWjson['hourly'][5]))
        self.assertTrue(OpenWeatherManager.has_rain(
            OWjson['hourly'][6]))

    def test_clouds(self):
        OWjson = json.load(open(os.path.join(fileDir, 'onecall.json')))
        self.assertFalse(OpenWeatherManager.is_cloudy(
            OWjson['hourly'][0]))
        self.assertTrue(OpenWeatherManager.is_cloudy(
            OWjson['hourly'][2]))

    def test_temp(self):
        OWjson = json.load(open(os.path.join(fileDir, 'onecall.json')))
        self.assertFalse(OpenWeatherManager.has_low_temp(
            OWjson['hourly'][0], 5.0))
        self.assertTrue(OpenWeatherManager.has_low_temp(
            OWjson['hourly'][0], 25.0))


if __name__ == '__main__':
    unittest.main()
