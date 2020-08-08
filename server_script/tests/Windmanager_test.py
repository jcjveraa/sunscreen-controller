
import unittest

from SunScreenServer.Windmanager import check_array_high_wind, check_last_25_minutes_had_high_winds
from SunScreenServer.GetSecrets import get_secrets

class WindmanagerTest(unittest.TestCase):
    secrets = get_secrets()

    test_json_string_true = '[{"id":"0EGR2Z6Z4CS9QN8WWNR5TTQKR5","value":"' + str(secrets['HIGH_WIND_DIRECT_MEASUREMENT'])+ '","feed_id":1408032,"feed_key":"wind","created_at":"2020-08-08T09:27:04Z","created_epoch":1596878824,"expiration":"2020-09-07T09:27:04Z"},{"id":"0EGR2YPTHQKHT5H2M4M765H1QM","value":"0.208333","feed_id":1408032,"feed_key":"wind","created_at":"2020-08-08T09:26:12Z","created_epoch":1596878772,"expiration":"2020-09-07T09:26:12Z"},{"id":"0EGR2Y2BE8XE15G50TDYCZSJWD","value":"0.125","feed_id":1408032,"feed_key":"wind","created_at":"2020-08-08T09:25:04Z","created_epoch":1596878704,"expiration":"2020-09-07T09:25:04Z"}]'
    test_json_string_false = '[{"id":"0EGR2Z6Z4CS9QN8WWNR5TTQKR5","value":"' + str(0) + '","feed_id":1408032,"feed_key":"wind","created_at":"2020-08-08T09:27:04Z","created_epoch":1596878824,"expiration":"2020-09-07T09:27:04Z"},{"id":"0EGR2YPTHQKHT5H2M4M765H1QM","value":"0.208333","feed_id":1408032,"feed_key":"wind","created_at":"2020-08-08T09:26:12Z","created_epoch":1596878772,"expiration":"2020-09-07T09:26:12Z"},{"id":"0EGR2Y2BE8XE15G50TDYCZSJWD","value":"0.125","feed_id":1408032,"feed_key":"wind","created_at":"2020-08-08T09:25:04Z","created_epoch":1596878704,"expiration":"2020-09-07T09:25:04Z"}]'

    def test_closing(self):
        self.assertTrue(check_array_high_wind([0,0,0,self.secrets['HIGH_WIND_DIRECT_MEASUREMENT']]))
        self.assertFalse(check_array_high_wind([0,0,0,self.secrets['HIGH_WIND_DIRECT_MEASUREMENT']-1]))

    def test_25_min(self):
        self.assertTrue(check_last_25_minutes_had_high_winds(test_json_string=self.test_json_string_true))
        self.assertFalse(check_last_25_minutes_had_high_winds(test_json_string=self.test_json_string_false))

if __name__ == '__main__':
    unittest.main()
