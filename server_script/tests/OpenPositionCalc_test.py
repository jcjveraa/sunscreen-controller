
import unittest
from os import listdir
from os.path import isfile, join

from SunScreenServer.GetSecrets import get_secrets
from SunScreenServer.OpenPosCalc import get_open_percentage_required, open_percentage_required, round_to_nearest
from SunScreenServer.SunPositionCalcs import DEG_TO_RAD


class OpenPosCalcTest(unittest.TestCase):

    secrets = get_secrets()

    def test_open_pos(self):
        self.assertEqual(int(24.46524406), open_percentage_required(49.83*DEG_TO_RAD, -1.158375025))

    def test_open_pos_with_adjustment(self):
        self.assertEqual(int(24.46524406) + 10, open_percentage_required(49.83*DEG_TO_RAD, -1.158375025, adjustment=10))


    def test_round_to_nearest(self):
        self.assertEqual(0, round_to_nearest(0, 50))
        self.assertNotEqual(0, round_to_nearest(1, 50))
        self.assertEqual(50, round_to_nearest(1, 50))
        self.assertEqual(50, round_to_nearest(50, 50))
        self.assertEqual(100, round_to_nearest(51, 50))

if __name__ == '__main__':
    unittest.main()
