
import unittest

from SunScreenServer import Windmanager
from SunScreenServer.GetSecrets import get_secrets


class WindmanagerTest(unittest.TestCase):
    secrets = get_secrets()

    def test_closing(self):
        self.assertTrue(Windmanager.check_array_high_wind([0,0,0,self.secrets['HIGH_WIND']]))
        self.assertFalse(Windmanager.check_array_high_wind([0,0,0,self.secrets['HIGH_WIND']-1]))

if __name__ == '__main__':
    unittest.main()
