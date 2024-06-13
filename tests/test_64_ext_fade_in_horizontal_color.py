import unittest
import testBase


class Extension(testBase.TestBase, unittest.TestCase):
    manip_func_name = "fade_in_horizontal"
    test_weight = 2

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"color": (255, 200, 100)})
