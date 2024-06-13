import unittest
import testBase2


class Extension(testBase2.TestBase2, unittest.TestCase):
    manip_func_name = "blend_other"
    test_weight = 5
    image_sets = [
        ("odd", "wider"),  # double overlapping
        ("wider", "odd"),
        ("taller", "odd"),  # completely contained
        ("odd", "taller"),
    ]
