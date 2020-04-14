import unittest
from SunScreenServer import OpenWeatherManager
class OWMTest(unittest.TestCase):

    def test_Kelvin_to_Celcius(self):
        self.assertEqual(OpenWeatherManager.kelvin_to_celcius(0), -273.15)
        self.assertNotEqual(OpenWeatherManager.kelvin_to_celcius(1), -270.15)

    def test_is_current_check(self):
        json = OpenWeatherManager.get_Open_Weather_JSON()
        self.assertTrue(OpenWeatherManager.is_current(json))
        self.assertFalse(OpenWeatherManager.is_current(json, -(5*60)))

    def test_next_forecast(self):
        json = OpenWeatherManager.get_Open_Weather_JSON()
        self.assertTrue('dt' in OpenWeatherManager.get_next_forecast(json))

if __name__ == '__main__':
    unittest.main()
