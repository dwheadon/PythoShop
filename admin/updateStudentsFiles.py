import glob
import os
import shutil
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWGRP, S_IWOTH, S_IWRITE

import students


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
            os.chmod(destination_file, S_IWRITE | S_IWGRP | S_IWOTH)
        except:
            pass
        shutil.copy(file, destination_file)
        os.chmod(destination_file, S_IREAD | S_IRGRP | S_IROTH)


files = [
    "__init__.py",
    "PythoShop.kv",
    "PythoShop.py",
    "PythoShopExports.py",
    "pythoshop.code-workspace",
]

examples_images = glob.glob("images/*")

vscode_files = [
    ".vscode-students/launch.json",
    # ".vscode-students/settings.json", # uncomment if want type checking
]

test_files = []
test_files += glob.glob("tests/testBase*")
test_files += glob.glob("tests/testFile*")
test_files += glob.glob("tests/testOrig*")
test_files += glob.glob("tests/testRun*")
test_files += glob.glob("tests/testTool*")
test_files += glob.glob("tests/config.py")
# Initially only release the first tests and then add others as you get to them
test_files += glob.glob("tests/test_0*")
# test_files += glob.glob("tests/test_1*")
# test_files += glob.glob("tests/test_2*")
# test_files += glob.glob("tests/test_3*")
# test_files += glob.glob("tests/test_4*")
# test_files += glob.glob("tests/test_5*")
# test_files += glob.glob("tests/test_6*")

for student_folder in students.STUDENT_FOLDERS:
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
        shutil.copy("ImageManipBlank.py", image_manip)
