import students
import glob
import shutil
import os

files = []
for student_folder in students.STUDENT_FOLDERS:
    student_file = '"' + student_folder + '/PythoShop/ImageManip.py"'
    files.append(student_file)

# Have to have compare50 installed: pip install compare50
os.system('compare50 ' + " ".join(files))
