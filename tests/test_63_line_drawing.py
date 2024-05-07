import unittest
import testBase


class Test(testBase.TestBase, unittest.TestCase):
    manip_func_name = "make_line_drawing"
    test_weight = 25

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"color": (0, 0, 0), "extra": "10"})
