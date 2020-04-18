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
        self.assertEqual(SunPositionCalcs.solar_hour_angle(1587236407, False, reference_time=(1587225607)), -45)
        self.assertAlmostEqual(SunPositionCalcs.solar_hour_angle(1586883340, reference_time=(1586883340)), 0)

    def test_declination(self):
        # https://www.esrl.noaa.gov/gmd/grad/solcalc/azel.html
        with self.subTest():
            self.assertAlmostEqual(11.15 , SunPositionCalcs.solar_declination(reference_time=1587225607)/ SunPositionCalcs.DEG_TO_RAD , 0)
        with self.subTest():
            self.assertAlmostEqual(-9.96  , SunPositionCalcs.solar_declination(reference_time=1603036807)/ SunPositionCalcs.DEG_TO_RAD , 0)
        with self.subTest():
            self.assertAlmostEqual(11.05  , SunPositionCalcs.solar_declination(reference_time=1587202773)/ SunPositionCalcs.DEG_TO_RAD , 0)

    def test_zenith(self):
        # https://www.esrl.noaa.gov/gmd/grad/solcalc/azel.html GIVES WRONG INFO!!!
        # use https://www.esrl.noaa.gov/gmd/grad/solcalc/
        LAT = 40.125 * SunPositionCalcs.DEG_TO_RAD
        # print(LAT)
        with self.subTest():
            self.assertAlmostEqual(0.65526833938, SunPositionCalcs.cosine_of_solar_zenith(1587236407, LAT, reference_time=1587225607), 2)
        # with self.subTest():
        #     self.assertAlmostEqual(math.cos(0.7745), math.cos(SunPositionCalcs.cosine_of_solar_zenith(1587236407, LAT, reference_time=1587225607)), 3)
        with self.subTest():
            self.assertAlmostEqual(math.sin(41.28* SunPositionCalcs.DEG_TO_RAD), SunPositionCalcs.cosine_of_solar_zenith(1597777478, LAT, reference_time=1597766407), 2)
        with self.subTest():
            self.assertAlmostEqual(math.sin(26.98* SunPositionCalcs.DEG_TO_RAD) , SunPositionCalcs.cosine_of_solar_zenith(1603046756, LAT, reference_time=1603036807), 2)

    def test_basecase_zenit(self):
        LAT = 40.125 * SunPositionCalcs.DEG_TO_RAD
        HRANG = -45 * SunPositionCalcs.DEG_TO_RAD
        DECL = 11.15 * SunPositionCalcs.DEG_TO_RAD
        term_1 = math.sin(LAT) * math.sin(DECL)
        term_2 = math.cos(LAT) * math.cos(DECL) * math.cos(HRANG)
        self.assertAlmostEqual(term_1 + term_2, 0.65526833938, 3)

    def test_azimuth(self):
        LAT = 40.125 * SunPositionCalcs.DEG_TO_RAD
        with self.subTest():
            self.assertAlmostEqual(113.33, SunPositionCalcs.solar_azimuth_compass(1587236407, LAT, reference_time=1587225607), 0)
        with self.subTest():
            self.assertAlmostEqual(132.98, SunPositionCalcs.solar_azimuth_compass(1603046756, LAT, reference_time=1603036807), 0)
        with self.subTest():
            self.assertAlmostEqual(203.1, SunPositionCalcs.solar_azimuth_compass(1603046756, LAT, reference_time=1603036807+4*3600), 0)
        with self.subTest():
            self.assertAlmostEqual(206.62, SunPositionCalcs.solar_azimuth_compass(1587209689, 52.529767 * SunPositionCalcs.DEG_TO_RAD, reference_time=1587214166), 0)

if __name__ == '__main__':
    unittest.main()
