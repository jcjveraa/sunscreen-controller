
import unittest

from SunScreenServer import SunManager



class SunManagerTEst(unittest.TestCase):

   def test_azimuth(self):
       self.assertTrue(SunManager.sun_not_on_window(0, 1, 5))
       self.assertFalse(SunManager.sun_not_on_window(2, 1, 5))

if __name__ == '__main__':
    unittest.main()
