import os
import pickle
import random
import unittest

import ImageManip
import tests.config as config

if __name__ == "__main__":
    # Pickle up the originals
    original_images = {}
    pickle_file_name = "testOriginals.pickle"
    for file_name in config.FILE_NAMES:
        file_name = file_name + ".bmp"
        file = open(os.path.join("images", file_name), "rb")
        original_images[file_name] = file.read()
        print("Pickling: " + file_name + " in " + pickle_file_name)
        file.close()
    pickle_file = open(pickle_file_name, "wb")
    pickle.dump(original_images, pickle_file)
    pickle_file.close()

    testSuite = unittest.defaultTestLoader.discover(".")
    for test in testSuite:
        if test.countTestCases() == 0:
            continue
        test_name = test._tests[0]._tests[0].manip_func_name
        test_args = test._tests[0]._tests[0].test_parameters
        test_image_sets = test._tests[0]._tests[0].image_sets
        args_name = ""
        for param, value in test_args.items():
            args_name += "_" + param + "_" + str(value)
        solution_images = {}
        pickle_file_name = test._tests[0]._tests[0].__module__ + ".pickle"
        if test_image_sets is None:
            test_image_sets = list([file_name] for file_name in config.FILE_NAMES)
        for original_file_names in test_image_sets:
            random.seed(0)  # make it predictably random
            original_files = []
            solution_file_name = test_name + args_name + "-" + "-".join(original_file_names) + ".bmp"
            solution_file = open(solution_file_name, "wb+")
            solution_file.write(original_images[original_file_names[0] + ".bmp"])
            original_files.append(solution_file)
            solution_file.seek(0)
            other_image = None
            if len(original_file_names) == 1:
                pass
            elif len(original_file_names) == 2:
                original_file_name = original_file_names[1] + ".bmp"
                other_image = open(os.path.join("images", original_file_name), "rb")
            else:
                raise (ValueError("Files for this test can be 1 or 2 files only"))
            testFunction = getattr(ImageManip, test_name)
            result = testFunction(*original_files, other_image=other_image, **test_args)
            if result is not None:
                solution_file.close()
                solution_file = open(solution_file_name, "wb+")
                result.seek(0)
                solution_file.write(result.read())
            solution_file.seek(0)
            solution_images[solution_file_name] = solution_file.read()
            print("Pickling: " + solution_file_name + " in " + pickle_file_name)
            solution_file.close()
        pickled_solution_images = open(pickle_file_name, "wb")
        pickle.dump(solution_images, pickled_solution_images)
        pickled_solution_images.close()
