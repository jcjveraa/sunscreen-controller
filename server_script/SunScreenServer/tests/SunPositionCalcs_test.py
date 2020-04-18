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
        # SunPositionCalcs.solar_hour_angle(1586883340, reference_time=(1586883340-12*3600))
        self.assertEqual(SunPositionCalcs.solar_hour_angle(1586883340, False, reference_time=(1586883340-12*3600)), -180)
        self.assertAlmostEqual(SunPositionCalcs.solar_hour_angle(1586883340, reference_time=(1586883340-12*3600)), -math.pi)
        self.assertEqual(SunPositionCalcs.solar_hour_angle(1586883340, False, reference_time=(1586883340+12*3600)), 180)
        self.assertAlmostEqual(SunPositionCalcs.solar_hour_angle(1586883340, reference_time=(1586883340)), 0)

    def test_declination(self):
        # https://www.esrl.noaa.gov/gmd/grad/solcalc/azel.html
        with self.subTest():
            self.assertAlmostEqual(11.15 * SunPositionCalcs.DEG_TO_RAD , SunPositionCalcs.solar_declination(reference_time=1587225607), 1)
        with self.subTest():
            self.assertAlmostEqual(-9.96 * SunPositionCalcs.DEG_TO_RAD , SunPositionCalcs.solar_declination(reference_time=1603036807), 1)
        with self.subTest():
            self.assertAlmostEqual(11.05 * SunPositionCalcs.DEG_TO_RAD , SunPositionCalcs.solar_declination(reference_time=1587202773), 1)

    def test_zenith(self):
        # https://www.esrl.noaa.gov/gmd/grad/solcalc/azel.html
        LAT = 40.125 * SunPositionCalcs.DEG_TO_RAD
        with self.subTest():
            self.assertAlmostEqual(0.7757, SunPositionCalcs.cosine_of_solar_zenith(1587236407, LAT, reference_time=1587225607), 3)
        with self.subTest():
            self.assertAlmostEqual(0.781, SunPositionCalcs.cosine_of_solar_zenith(1597777478, LAT, reference_time=1597766407), 3)
        with self.subTest():
            self.assertAlmostEqual(0.5642 , SunPositionCalcs.cosine_of_solar_zenith(1603046756, LAT, reference_time=1603036807), 3)


if __name__ == '__main__':
    unittest.main()
