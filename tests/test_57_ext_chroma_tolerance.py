import unittest
import testBase2


class Extension(testBase2.TestBase2, unittest.TestCase):
    manip_func_name = "chroma_overlay"
    test_weight = 2
    image_sets = [
        ("square", "gfish"),
    ]

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"clicked_coordinate": (20, 30), "color": (0, 255, 0), "extra": "5"})
