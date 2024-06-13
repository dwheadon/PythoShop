import unittest
import testBase2


class Extension(testBase2.TestBase2, unittest.TestCase):
    manip_func_name = "chroma_overlay"
    test_weight = 5
    image_sets = [
        ("square", "gfish"),
    ]

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"color": (0, 255, 0)})
