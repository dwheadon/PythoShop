import unittest
import testTool


class Test(testTool.Test, unittest.TestCase):
    manip_func_name = "change_pixel"
    image_sets = [
        ["square"],
        ["wider"],
        ["taller"],
        ["odd"],
        ["even"],
        ["bmpV1"],
    ]
    test_weight = 25

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters.update({"clicked_coordinate": (0, 0), "color": (255, 0, 255)})
