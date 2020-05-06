
import unittest
from os import listdir
from os.path import isfile, join

from SunScreenServer.GetSecrets import get_secrets
from SunScreenServer.OpenPosCalc import get_open_percentage_required, open_percentage_required
from SunScreenServer.SunPositionCalcs import DEG_TO_RAD


class OpenPosCalcTest(unittest.TestCase):

    secrets = get_secrets()

    def test_open_pos(self):
        self.assertEqual(int(24.46524406), open_percentage_required(49.83*DEG_TO_RAD, -1.158375025))

if __name__ == '__main__':
    unittest.main()
