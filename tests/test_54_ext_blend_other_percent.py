import unittest
import testBase2


class Extension(testBase2.TestBase2, unittest.TestCase):
    manip_func_name = "blend_other"
    test_weight = 2
    image_sets = [
        ("odd", "wider"),  # double overlapping
        ("wider", "odd"),
        ("taller", "odd"),  # completely contained
        ("odd", "taller"),
    ]

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"extra": "0.25"})
