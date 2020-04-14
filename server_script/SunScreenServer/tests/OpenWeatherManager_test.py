import unittest




class OWMTest(unittest.TestCase):

    def test_Kelvin_to_Celcius(self):
        OpenWeatherManager
        owm = OpenWeatherManager()
        self.assertEqual(owm.kelvin_to_celcius(0), -273.15)
        self.assertNotEqual(owm.kelvin_to_celcius(1), -270.15)

    def test_is_current_check(self):
        owm = OpenWeatherManager()
        owm.get_Open_Weather_JSON()
        self.assertTrue(owm.oncecall_is_current())
        self.assertFalse(owm.oncecall_is_current(-(5*60)))

    def test_next_forecast(self):
        owm = OpenWeatherManager()
        self.assertTrue('dt' in owm.get_next_forecast())

if __name__ == '__main__':
    unittest.main()
