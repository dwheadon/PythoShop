import unittest
import testBase2


class Test(testBase2.TestBase2, unittest.TestCase):
    manip_func_name = "blend_other"
    test_weight = 33
    image_sets = [
        ("evenB1", "evenB2"),
        ("oddB1", "oddB2"),  # requires padding
    ]
