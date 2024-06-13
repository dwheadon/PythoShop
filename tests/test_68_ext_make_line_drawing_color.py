import unittest
import testBase


class Extension(testBase.TestBase, unittest.TestCase):
    manip_func_name = "make_line_drawing"
    test_weight = 1

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"extra": "10"})
