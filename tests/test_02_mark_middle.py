import unittest
import testTool


class Test(testTool.Test, unittest.TestCase):
    manip_func_name = "mark_middle"
    image_sets = [
        ["pad1"],
        ["pad3"],
        ["odd"],
    ]
    test_weight = 50
