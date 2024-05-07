import unittest
import pickle
import tempfile
import inspect
import tests.config as config
import os
import importlib.util
import random
import signal
import platform
import io


class TestTimeoutException(Exception):
    pass


class TestTimeout:
    def __init__(self, seconds, error_message=None):
        if error_message is None:
            error_message = 'test timed out after {}s.'.format(seconds)
            self.seconds = seconds
            self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TestTimeoutException(self.error_message)

    def __enter__(self):
        if not "Windows" in platform.system():
            signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not "Windows" in platform.system():
            signal.alarm(0)


class TestBase:
    original_images = {}
    solution_images = {}
    test_parameters = {
        "color": (238, 0, 119),
        "extra": "extra parameters..."
    }
    manip_func_name = None
    manip_func = None
    test_weight = 0
    image_sets = None
    manip_module = None
    num_image_parameters = 1
    tolerance = 1 # may want to change this depending on how strict you want to be with rounding

    def __init__(self, test):
        super().__init__(test)
        self.__class__.test_parameters = self.__class__.test_parameters.copy()
        if self.image_sets is None:
            self.image_sets = list([file_name] for file_name in config.FILE_NAMES)

    def get_info(self, image):
        image.seek(10)
        fpp = int.from_bytes(image.read(4), "little")
        image.seek(18)
        width = int.from_bytes(image.read(4), "little")
        height = int.from_bytes(image.read(4), "little")
        colorp = int.from_bytes(image.read(2), "little")
        bpp = int.from_bytes(image.read(2), "little")
        if bpp != 24:
            self.assertTrue(False, "Unsupported bits per pixel")
        compression = int.from_bytes(image.read(4), "little")
        if compression != 0:
            self.assertTrue(False, "Unsupported compression")
        row_size = width * 3
        # Rows need to be padded to a multiple of 4 bytes
        row_padding = 0
        if row_size % 4 != 0:
            row_padding = 4 - row_size % 4
            row_size += row_padding
        return fpp, width, height, row_size, row_padding

    def compare_headers(self, image1, image2):
        """ image1 is the reference (correct) image """
        fpp1, width1, height1, row_size1, pad1 = self.get_info(image1)
        fpp2, width2, height2, row_size2, pad2 = self.get_info(image2)
        image1.seek(0)
        image2.seek(0)
        header_field1 = image1.read(2)
        header_field2 = image2.read(2)
        self.assertTrue(header_field1 == header_field2, "The header field is incorrect.\n  Should be: " + header_field1.hex() + "\n   Actually: " + header_field2.hex())
        self.assertTrue(width1 == width2, "The width is incorrect.\n  Should be: " + str(width1) + "\n   Actually: " + str(width2))
        self.assertTrue(height1 == height2, "The height is incorrect.\n  Should be: " + str(height1) + "\n   Actually: " + str(height2))

    @classmethod
    def get_parameter_str(cls):
        parameter_str = ""
        for parameter_name, parameter_value in cls.test_parameters.items():
            parameter_str += "_" + parameter_name + "_" + str(parameter_value)
        return parameter_str

    @classmethod
    def setUpClass(cls):
        pickled_originals = open("testOriginals.pickle", "rb")
        cls.original_images = pickle.load(pickled_originals)
        pickled_originals.close()
        try:
            if "IMAGE_MANIP" in os.environ:
                spec = importlib.util.spec_from_file_location("ImageManip", os.environ["IMAGE_MANIP"] + "/ImageManip.py")
            else:
                spec = importlib.util.spec_from_file_location("ImageManip", os.getcwd() + "/../ImageManip.py")
            cls.manip_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.manip_module)
            if cls.manip_func_name in dir(cls.manip_module):
                cls.manip_func = getattr(cls.manip_module, cls.manip_func_name)
            else:
                raise unittest.SkipTest(cls.__module__ + ": function " + cls.manip_func_name + "() is not available to test")
        except SyntaxError:
            raise unittest.SkipTest(cls.__module__ + ": ImageManip.py has a syntax error and can't be tested")
        positional_args = inspect.getfullargspec(cls.manip_func.__wrapped__).args.copy()
        # starting from the end, remove all the args that are handled by kwargs so we're left with just positional args
        while positional_args[-1] in cls.test_parameters:
            positional_args = positional_args[:-1]
        # what should be left is just the image parameters
        if len(positional_args) < cls.num_image_parameters:
            raise unittest.SkipTest(cls.__module__ + ": function " + cls.manip_func_name + "() does not take " + str(len(cls.test_parameters) + cls.num_image_parameters) + " parameters.")
        pickled_solutions_file_name = cls.__module__ + ".pickle"
        pickled_solutions = open(pickled_solutions_file_name, "rb")
        cls.solution_images = pickle.load(pickled_solutions)
        pickled_solutions.close()

    def test_images(self):
        with TestTimeout(10):
            for image_set in self.image_sets:
                image = image_set[0]
                with self.subTest(i=image_set):
                    random.seed(0)  # make it predictably random
                    orig_file_name = image + ".bmp"
                    test_file_name = self.manip_func_name + self.get_parameter_str() + "-" + image + ".bmp"
                    static_manip_func = getattr(self.manip_module, self.manip_func_name)
                    with tempfile.TemporaryFile() as image_file:
                        image_file.write(self.original_images[orig_file_name])
                        try:
                            result = static_manip_func(image_file, **self.test_parameters)
                        except Exception as e:
                            self.assertTrue(False, "Running on " + orig_file_name + " casused an exception: " + str(e))
                        if result == None:
                            result = image_file
                        self.assertTrue(type(result) == io.BytesIO or type(result) == io.BufferedRandom)
                        solution_image = io.BytesIO(self.solution_images[test_file_name])
                        self.compare_headers(solution_image, result)
                        fpp1, width1, height1, row_size1, pad1 = self.get_info(solution_image)
                        fpp2, width2, height2, row_size2, pad2 = self.get_info(result)
                        for row in range(height1):
                            for pixel in range(width1):
                                try:
                                    solution_image.seek(fpp1 + row_size1 * row + 3 * pixel)
                                    result.seek(fpp2 + row_size2 * row + 3 * pixel)
                                    correct_b, correct_g, correct_r = solution_image.read(3)
                                    actual_b, actual_g, actual_r = result.read(3)
                                except:
                                    self.assertTrue(False, "Pixel at (" + str(pixel) + ", " + str(row) + ") could not be read.")
                                if actual_b < correct_b - self.tolerance or actual_b > correct_b + self.tolerance \
                                    or actual_g < correct_g - self.tolerance or actual_g > correct_g + self.tolerance \
                                    or actual_r < correct_r - self.tolerance or actual_r > correct_r + self.tolerance:
                                    pixel_index = fpp1 + row_size1 * row + 3 * pixel
                                    original_b, original_g, original_r = self.original_images[orig_file_name][pixel_index:pixel_index + 3]
                                    self.assertTrue(False, "Pixel at (" + str(pixel) + ", " + str(row) + ") is incorrect. \nOriginal was " + str([original_b, original_g, original_r]) + "\nIt should be " + str([correct_b, correct_g, correct_r]) + "\nBut actually " + str([actual_b, actual_g, actual_r]))
                            solution_image.seek(pad1, 1)
                            result.seek(pad2, 1)
