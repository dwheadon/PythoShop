import unittest
import testTool


class Test(testTool.Test, unittest.TestCase):
    manip_func_name = "draw_hline"
    test_weight = 50
