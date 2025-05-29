import io
import random
import shutil
import subprocess
import sys
import tempfile

import testBase


class TestBase2(testBase.TestBase):
    """
    The functions that this tests take two images and makes a new
    image which gets returned from the function
    """

    num_image_parameters = 2

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters = self.__class__.test_parameters.copy()

    def test_images(self):
        already_showed_failed_exemple = False
        if self.image_sets is None:
            assert False
        for image1_name, image2_name in self.image_sets:
            with self.subTest(i=image1_name + "_&_" + image2_name), tempfile.TemporaryFile() as image1, tempfile.TemporaryFile() as image2:
                random.seed(0)  # make it predictably random
                image1_file_name = image1_name + ".bmp"
                image2_file_name = image2_name + ".bmp"
                test_file_name = self.manip_func_name + self.get_parameter_str() + "-" + image1_name + "-" + image2_name + ".bmp"
                static_manip_func = getattr(self.manip_module, self.manip_func_name)
                image1.write(self.original_images[image1_file_name])
                image2.write(self.original_images[image2_file_name])
                try:
                    with testBase.TestTimeout(2):
                        result = static_manip_func(image1, other_image=image2, **self.test_parameters)
                except Exception as e:
                    self.assertTrue(False, "Running on " + image1_file_name + " and " + image2_file_name + " casused an exception: " + str(e))
                if result == None:
                    result = image1
                self.assertTrue(type(result) == io.BytesIO or type(result) == io.BufferedRandom or type(result) == tempfile._TemporaryFileWrapper)
                solution_image = io.BytesIO(self.solution_images[test_file_name])
                self.compare_headers(solution_image, result)
                fpp1, width1, height1, row_size1, pad1 = self.get_info(solution_image)
                fpp2, width2, height2, row_size2, pad2 = self.get_info(result)
                for row in range(height1):
                    for pixel in range(width1):
                        try:
                            solution_image.seek(fpp1 + row_size1 * row + 3 * pixel)
                            correct_b, correct_g, correct_r = solution_image.read(3)
                            result.seek(fpp2 + row_size2 * row + 3 * pixel)
                            actual_b, actual_g, actual_r = result.read(3)
                        except:
                            self.assertTrue(False, "Pixel at (" + str(pixel) + ", " + str(row) + ") could not be read.")
                        if (
                            actual_b < correct_b - self.tolerance
                            or actual_b > correct_b + self.tolerance
                            or actual_g < correct_g - self.tolerance
                            or actual_g > correct_g + self.tolerance
                            or actual_r < correct_r - self.tolerance
                            or actual_r > correct_r + self.tolerance
                        ):
                            pixel_index = fpp1 + row_size1 * row + 3 * pixel
                            original1_b, original1_g, original1_r = self.original_images[image1_file_name][pixel_index : pixel_index + 3]
                            original2_b, original2_g, original2_r = self.original_images[image2_file_name][pixel_index : pixel_index + 3]
                            # open the two images for visual inspection
                            if not already_showed_failed_exemple:
                                try:
                                    with tempfile.NamedTemporaryFile(
                                        suffix=".bmp", prefix=self.__module__ + "_" + image1_name + "," + image2_name + "_", delete=False
                                    ) as student_image_file, tempfile.NamedTemporaryFile(
                                        suffix=".bmp", prefix="solution_" + self.__module__ + "_" + image1_name + "," + image2_name + "_", delete=False
                                    ) as solution_image_file:
                                        # result.flush()
                                        result.seek(0)
                                        shutil.copyfileobj(result, student_image_file)
                                        student_image_file.flush()
                                        # solution_image.flush()
                                        solution_image.seek(0)
                                        shutil.copyfileobj(solution_image, solution_image_file)
                                        solution_image_file.flush()
                                        subprocess.run_during_test(["open", "-a", "Preview", student_image_file.name, solution_image_file.name], check=True)
                                        already_showed_failed_exemple = True
                                except Exception as e:
                                    pass
                            self.assertTrue(
                                False,
                                "Pixel at ("
                                + str(pixel)
                                + ", "
                                + str(row)
                                + ") is incorrect. \nOriginals were "
                                + str([original1_b, original1_g, original1_r])
                                + " and "
                                + str([original2_b, original2_g, original2_r])
                                + "\nIt should be "
                                + str([correct_b, correct_g, correct_r])
                                + "\nBut actually "
                                + str([actual_b, actual_g, actual_r]),
                            )
                    solution_image.seek(pad1, 1)
                    result.seek(pad2, 1)
