import json
import math
import os
import time
import unittest

from SunScreenServer import SunPositionCalcs

fileDir = os.path.dirname(os.path.abspath(__file__))


class SolarTest(unittest.TestCase):

    def test_hour_angle(self):
        # OWjson = json.load(open(os.path.join(fileDir, 'onecall.json')))
        SunPositionCalcs.current_sun_hour_angle(1586883340, reference_time=(1586883340-12*3600))
        self.assertEqual(SunPositionCalcs.current_sun_hour_angle(1586883340, reference_time=(1586883340-12*3600)), -180)
        self.assertAlmostEqual(SunPositionCalcs.current_sun_hour_angle(1586883340, True ,reference_time=(1586883340-12*3600)), -math.pi)
        self.assertEqual(SunPositionCalcs.current_sun_hour_angle(1586883340, reference_time=(1586883340+12*3600)), 180)
        self.assertAlmostEqual(SunPositionCalcs.current_sun_hour_angle(1586883340, True ,reference_time=(1586883340)), 0)

    def test_declination(self):
        # https://www.esrl.noaa.gov/gmd/grad/solcalc/azel.html
        with self.subTest():
            self.assertAlmostEqual(11.15 * SunPositionCalcs.DEG_TO_RAD , SunPositionCalcs.solar_declination(reference_time=1587196852), 1)
        with self.subTest():
            self.assertAlmostEqual(-9.96 * SunPositionCalcs.DEG_TO_RAD , SunPositionCalcs.solar_declination(reference_time=1603008052), 1)


if __name__ == '__main__':
    unittest.main()
