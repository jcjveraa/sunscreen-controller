from SunScreenServer.tools import binarize_bool_array
import unittest


class ToolsTest(unittest.TestCase):

    def test_binarize_bool_array(self):
        self.assertEqual(binarize_bool_array([True, True]), 3)
        self.assertEqual(binarize_bool_array([False, True]), 1)
        self.assertEqual(binarize_bool_array([True, False]), 2)
        self.assertEqual(binarize_bool_array([False, False]), 0)
        self.assertEqual(binarize_bool_array([True, False, False]), 4)
        self.assertEqual(binarize_bool_array([False, True, False, False, False]), 8)
        self.assertEqual(binarize_bool_array([False,True, False, False, True]), 9)
        self.assertNotEqual(binarize_bool_array([True, False]), 0)
