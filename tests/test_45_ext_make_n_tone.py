import unittest
import testBase


class Extension(testBase.TestBase, unittest.TestCase):
    manip_func_name = "make_n_tone"
    test_weight = 20

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"color": (255, 255, 255), "extra": "6"})
