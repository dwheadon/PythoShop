import unittest
import testBase


class Extension(testBase.TestBase, unittest.TestCase):
    manip_func_name = "make_two_tone"
    test_weight = 2

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"color": (255, 255, 0)})
        self.image_sets.remove(["dark"]) # just all one color
