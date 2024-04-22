import students
import glob
import shutil
import os
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWRITE, S_IWGRP, S_IWOTH

import tests.config as config


def copy_readonly_files(files, destination_folder):
        # print("Verifying folder exists...")
        try:
            os.makedirs(destination_folder)
        except FileExistsError:
            pass
        # print("Copying to " + destination_folder)
        for file in files:
            # print("    Copying " + str(file))
            destination_file = os.path.join(destination_folder, os.path.basename(file))
            try:
                os.chmod(destination_file, S_IWRITE|S_IWGRP|S_IWOTH)
            except:
                 pass
            shutil.copy(file, destination_file)
            os.chmod(destination_file, S_IREAD|S_IRGRP|S_IROTH)

files = [
     '/Users/danwheadon/Projects/PythoShop/__init__.py',
     '/Users/danwheadon/Projects/PythoShop/PythoShop.kv',
     '/Users/danwheadon/Projects/PythoShop/PythoShop.py',
     '/Users/danwheadon/Projects/PythoShop/PythoShopExports.py',
     '/Users/danwheadon/Projects/PythoShop/uchicago.bmp',
]

examples_images = glob.glob("/Users/danwheadon/Projects/PythoShop/images/*")

vscode_files = [
     '/Users/danwheadon/Projects/PythoShop/.vscode-students/launch.json',
]

test_files = []
test_files +=  glob.glob("/Users/danwheadon/Projects/PythoShop/tests/testBase*")
test_files += glob.glob("/Users/danwheadon/Projects/PythoShop/tests/testFile*")
test_files += glob.glob("/Users/danwheadon/Projects/PythoShop/tests/testOrig*")
test_files += glob.glob("/Users/danwheadon/Projects/PythoShop/tests/testRun*")
test_files += glob.glob("/Users/danwheadon/Projects/PythoShop/tests/testTool*")
test_files += glob.glob("/Users/danwheadon/Projects/PythoShop/tests/config.py")
# test_files += glob.glob("/Users/danwheadon/Projects/PythoShop/tests/images/*")
test_files += glob.glob("/Users/danwheadon/Projects/PythoShop/tests/test_0*")
test_files += glob.glob("/Users/danwheadon/Projects/PythoShop/tests/test_1*")
test_files += glob.glob("/Users/danwheadon/Projects/PythoShop/tests/test_2*")
test_files += glob.glob("/Users/danwheadon/Projects/PythoShop/tests/test_3*")
test_files += glob.glob("/Users/danwheadon/Projects/PythoShop/tests/test_4*")
test_files += glob.glob("/Users/danwheadon/Projects/PythoShop/tests/test_5*")
test_files += glob.glob("/Users/danwheadon/Projects/PythoShop/tests/test_6*")
# for file in config.FILE_NAMES:
#     files += ["./"+file+".bmp"]

for student_folder in students.student_folders:
    student_folder = os.path.join(student_folder, "PythoShop")
    student_vscode_folder = os.path.join(student_folder, ".vscode")
    student_test_folder = os.path.join(student_folder, "tests")
    student_images_folder = os.path.join(student_folder, "images")
    copy_readonly_files(files, student_folder)
    copy_readonly_files(vscode_files, student_vscode_folder)
    copy_readonly_files(test_files, student_test_folder)
    copy_readonly_files(examples_images, student_images_folder)
    image_manip = os.path.join(student_folder, "ImageManip.py")
    if not os.path.exists(image_manip):
        shutil.copy('/Users/danwheadon/Projects/PythoShop/ImageManipBlank.py', image_manip)
