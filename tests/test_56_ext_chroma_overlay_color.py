import unittest
import testBase2


class Extension(testBase2.TestBase2, unittest.TestCase):
    manip_func_name = "chroma_overlay"
    test_weight = 10
    image_sets = [
        ("square", "bfish"),
    ]

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"color": (0, 240, 240)})
