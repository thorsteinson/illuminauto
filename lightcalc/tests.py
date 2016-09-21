import unittest

from lightcalc import LightCalc
import numpy as np

class TestType(unittest.TestCase):
    def setUp(self):
        self.validNPArray = np.ones([500, 500, 3], dtype=int)

    def test_only_numpy_arrays(self):
        with self.assertRaises(TypeError):
            LightCalc('hello')
        with self.assertRaises(TypeError):
            LightCalc(1)
        with self.assertRaises(TypeError):
            LightCalc({})
        with self.assertRaises(TypeError):
            LightCalc(object())
        
        self.assertIsInstance(LightCalc(self.validNPArray), LightCalc)

    def test_img_dimension(self):
        with self.assertRaises(TypeError):
            LightCalc(np.empty([3, 4, 4, 5]))
        with self.assertRaises(TypeError):
            LightCalc(np.empty([5]))

    def test_3_color_channels(self):
        with self.assertRaises(TypeError):
            LightCalc(np.empty([3, 3, 4]))
        with self.assertRaises(TypeError):
            LightCalc(np.empty([3, 3, 1]))

if __name__ == '__main__':
    unittest.main()