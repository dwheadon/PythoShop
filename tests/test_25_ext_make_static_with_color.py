import unittest
import testBase


class Extension(testBase.TestBase, unittest.TestCase):
    manip_func_name = "make_static"
    test_weight = 10

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"color": (255, 200, 0)})
