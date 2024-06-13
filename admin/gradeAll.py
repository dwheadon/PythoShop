import glob
import importlib.util
import io
import os
import subprocess
import sys
import unittest

import students

test_files = glob.glob("test_0*.py")
test_files += glob.glob("test_1*.py")
test_files += glob.glob("test_2*.py")
test_files += glob.glob("test_3*.py")
test_files += glob.glob("test_4*.py")
test_files += glob.glob("test_5*.py")
test_files += glob.glob("test_6*.py")
test_files.sort()


def dummyInput(prompt=None):
    raise RuntimeError("You should not be calling the input function within your manipulation functions (only in __main__)")


def dummyRun(args, **kwargs):
    raise RuntimeError("You should not be calling the subprocess.run function within your manipulation functions (only in __main__)")


sys.modules["subprocess"].run = dummyRun
sys.modules["builtins"].input = dummyInput


class TestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.separator1 = "\n" + self.separator1
        self.points_total = 0
        self.tests = []

    def addPoints(self, test):
        # assert not hasattr(test, 'test_weight'), "Test " + str(test) + " doesn't have a weight"
        assert test.test_weight != 0, "Test " + str(test) + " has zero weight"
        assert type(test).__name__ == "Test" or type(test).__name__ == "Extension", "Test " + str(test) + ' is not named "Test" or "Extension"'
        if type(test).__name__ == "Test":
            self.points_total += test.test_weight

    def startTest(self, test):
        self.addPoints(test)
        self.tests.append(test)
        super().startTest(test)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        # What a hack but I can't see any other way to get this
        skipped_module_name = test.description[test.description.find("(") + 1 : test.description.find(".")]
        skipped_class_name = test.description[test.description.find(".") + 1 : test.description.find(")")]
        if skipped_class_name == "Test":
            skipped_module = __import__(skipped_module_name)
            if skipped_class_name in dir(skipped_module):
                skipped_class = getattr(skipped_module, skipped_class_name)
                self.points_total += skipped_class.test_weight


if __name__ == "__main__":
    print("\tTotal\t", end="")
    for test_file in test_files:
        test_package = test_file[: test_file.find(".")]
        print(test_package, end="\t")
    print("")
    for student_folder in students.student_folders:
        orig_stdout = sys.stdout
        print("Testing: " + student_folder, file=sys.stderr)
        student = student_folder.split("/")[-1]
        sys.stdout = io.StringIO()
        os.environ["IMAGE_MANIP"] = student_folder + "/PythoShop"
        os.environ["PYTEST_TIMEOUT"] = "2"
        testSuite = unittest.defaultTestLoader.discover(".")
        testProgram = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
        testProgram.resultclass = TestResult
        testResults = testProgram.run(testSuite)
        points_total = 0
        points_earned = 0
        tests_passed = []
        tests_partial = []
        tests_failed = []
        for test in testResults.tests:
            num_sub_tests = len(test.image_sets)
            sub_failures = [x for x in testResults.failures if x[0].test_case == test]
            num_sub_failures = len(sub_failures)
            num_sub_success = num_sub_tests - num_sub_failures
            percentage = 0
            if num_sub_failures == 0:
                tests_passed.append(test.__module__)
                percentage = 1.0
            elif num_sub_success > 0:
                tests_partial.append(test.__module__)
                # Get ~80% if passed at least one
                percentage = 0.75 + 0.25 * num_sub_success / num_sub_tests
            else:
                tests_failed.append(test.__module__)
                percentage = 0
            points = percentage * test.test_weight
            points_earned += points
        points_total = int(1.15 * testResults.points_total)
        if points_total > 0:
            grade = round(100 * points_earned / points_total)
        else:
            grade = 0
        grade_str = str(grade)
        sys.stdout = orig_stdout
        print(student + "\t" + grade_str, end="\t")
        sys.stdout = io.StringIO()

        points_total = int(1.15 * testResults.points_total)
        if points_total > 0:
            grade = round(100 * points_earned / points_total)
        else:
            grade = 0
        grade_str = str(grade)
        sys.stdout = orig_stdout
        for test_file in test_files:
            test_package = test_file[: test_file.find(".")]
            test_module = __import__(test_package)
            # spec = importlib.util.spec_from_file_location(test_package, student_folder + "/" + test_file)
            # test_module = importlib.util.module_from_spec(spec)
            # spec.loader.exec_module(test_module)
            # test_module = __import__(test_file)
            if "Test" in dir(test_module):
                test_class_name = "Test"
            elif "Extension" in dir(test_module):
                test_class_name = "Extension"
            test_class = getattr(test_module, test_class_name)
            test = test_class("test_images")
            # test.test_images()
            # points_total += test_class.test_weight
            if test in testResults.tests:
                num_sub_tests = len(test.image_sets)
                sub_failures = [x for x in testResults.failures if x[0].test_case == test]
                num_sub_failures = len(sub_failures)
                num_sub_success = num_sub_tests - num_sub_failures
                percentage = 0.0
                if num_sub_failures == 0:
                    tests_passed.append(test.__module__)
                    percentage = 1.0
                elif num_sub_success > 0:
                    tests_partial.append(test.__module__)
                    # Get ~80% if passed at least one
                    percentage = 0.75 + 0.25 * num_sub_success / num_sub_tests
                else:
                    tests_failed.append(test.__module__)
                    percentage = 0.0
            else:
                percentage = 0.0
            print(round(percentage, 1), end="\t")
        #     test = test_file[:-3]
        #     if test in testResults.testsPassed:
        #         print(1.0, end="\t")
        #     elif test in testResults.testsPartial:
        #         print(0.8, end="\t")
        #     elif test in testResults.testsFailed:
        #         print(0.1, end="\t")
        #     else:
        #         print(0.0, end="\t")
        print("")
