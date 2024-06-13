import unittest
import testBase2


class Test(testBase2.TestBase2, unittest.TestCase):
    manip_func_name = "chroma_overlay"
    test_weight = 33
    image_sets = [
        ("evenC1", "evenC2"),
        ("oddC1", "oddC2"),  # requires padding
    ]

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"color": (0, 255, 0)})
