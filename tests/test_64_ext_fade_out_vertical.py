import unittest
import testBase


class Extension(testBase.TestBase, unittest.TestCase):
    manip_func_name = "fade_out_vertical"
    test_weight = 1

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"color": (0, 0, 0)})
