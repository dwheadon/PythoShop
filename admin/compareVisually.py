import importlib.util
import inspect
import io
import os
import pickle
import shutil
import subprocess
import tempfile
import traceback

# For testing student's code to see the visual output compared to the solution to see if it looks mostly correct
# Requires you to have the correct reference solution
# Designed for Mac only (could be made to work on Windows with some minor tweaks)
# Warning: this will open a lot of "Preview" windows but you can comment out some of the tests if you don't want to run everything

# Test name, test function name, image names, other parameters
tests = [
    ("Pixel", "change_pixel", ["dark.bmp"], {"clicked_coordinate": (12, 25)}),
    ("Middle", "mark_middle", ["dark.bmp"], {}),
    ("Hline", "draw_hline", ["flower.bmp"], {}),
    ("HlinePosition", "draw_hline", ["flower.bmp"], {"clicked_coordinate": (200, 10)}),
    ("HlineThickness", "draw_hline", ["flower.bmp"], {"clicked_coordinate": (200, 10), "extra": "5"}),
    ("CenteredHline", "draw_centered_hline", ["flower.bmp"], {}),
    ("CenteredHlineThick", "draw_centered_hline", ["flower.bmp"], {"extra": "21"}),
    ("Vline", "draw_vline", ["flower.bmp"], {}),
    ("VlinePad", "draw_vline", ["pad1.bmp"], {}),
    ("VlinePosition", "draw_vline", ["flower.bmp"], {"clicked_coordinate": (150, 10)}),
    ("VlineThickness", "draw_vline", ["flower.bmp"], {"clicked_coordinate": (150, 10), "extra": "21"}),
    ("CenteredVline", "draw_centered_vline", ["flower.bmp"], {}),
    ("CenteredVlineThick", "draw_centered_vline", ["flower.bmp"], {"extra": "21"}),
    ("Borders", "borders", ["phoenix.bmp"], {}),
    ("BordersThick", "borders", ["phoenix.bmp"], {"extra": "21"}),
    ("DrawSloping", "draw_sloping_lines", ["wider.bmp"], {}),
    ("X", "draw_x", ["neptune.bmp"], {"clicked_coordinate": (150, 80)}),
    ("XRadius", "draw_x", ["neptune.bmp"], {"clicked_coordinate": (150, 80), "extra": "10"}),
    ("XedHLine", "draw_x_hline", ["neptune.bmp"], {"clicked_coordinate": (150, 80), "extra": "10"}),
    ("XedVLine", "draw_x_hline", ["neptune.bmp"], {"clicked_coordinate": (150, 80), "extra": "10"}),
    ("DrawBisectingDiagonals", "draw_bisecting_diagonals", ["flower.bmp"], {}),
    ("Fill", "fill", ["small_bear.bmp"], {"color": (255, 0, 0)}),
    ("FillColor", "fill", ["small_bear.bmp"], {"color": (255, 255, 0)}),
    ("FillPad", "fill", ["pad1.bmp"], {"color": (255, 0, 0)}),
    ("Static", "make_static", ["flower.bmp"], {}),
    ("StaticColor", "make_static", ["flower.bmp"], {"color": (120, 0, 255), "extra": "30"}),
    ("RemoveRed", "remove_red", ["flower.bmp"], {}),
    ("RemoveGreen", "remove_green", ["flower.bmp"], {}),
    ("RemoveBlue", "remove_blue", ["flower.bmp"], {}),
    ("MaxRed", "max_red", ["flower.bmp"], {}),
    ("MaxGreen", "max_green", ["flower.bmp"], {}),
    ("MaxBlue", "max_blue", ["flower.bmp"], {}),
    ("OnlyRed", "only_red", ["flower.bmp"], {}),
    ("OnlyGreen", "only_green", ["flower.bmp"], {}),
    ("OnlyBlue", "only_blue", ["flower.bmp"], {}),
    ("Lighten", "lighten", ["flower.bmp"], {}),
    ("LightenMultiplier", "lighten", ["flower.bmp"], {"extra": "5"}),
    ("Darken", "darken", ["flower.bmp"], {}),
    ("DarkenMultiplier", "darken", ["flower.bmp"], {"extra": "0.2"}),
    ("Gray", "make_gray", ["flower.bmp"], {}),
    ("DrawGray", "draw_gray", ["flower.bmp"], {"clicked_coordinate": (150, 80), "extra": "30"}),
    ("Negate", "negate", ["flower.bmp"], {}),
    ("NegateBlue", "negate_blue", ["flower.bmp"], {}),
    ("NegateGreen", "negate_green", ["flower.bmp"], {}),
    ("NegateRed", "negate_red", ["flower.bmp"], {}),
    ("SwapBRG", "swap_brg", ["flower.bmp"], {}),
    ("SwapGRB", "swap_grb", ["flower.bmp"], {}),
    ("SwapGBR", "swap_gbr", ["flower.bmp"], {}),
    ("SwapRBG", "swap_rbg", ["flower.bmp"], {}),
    ("SwapRGB", "swap_rgb", ["flower.bmp"], {}),
    ("Grayify", "grayify", ["flower.bmp"], {}),
    ("Redify", "redify", ["flower.bmp"], {}),
    ("Greenify", "greenify", ["flower.bmp"], {}),
    ("Blueify", "blueify", ["flower.bmp"], {}),
    ("Magentify", "magentify", ["flower.bmp"], {}),
    ("Intensify", "intensify", ["flower.bmp"], {}),
    ("IntensifyPartial", "intensify", ["flower.bmp"], {"extra": "0.2"}),
    ("TwoTone", "make_two_tone", ["flower.bmp"], {}),
    ("TwoToneCustom", "make_two_tone", ["flower.bmp"], {"color": (255, 0, 0), "extra": "0, 0, 255"}),
    ("FourTone", "make_four_tone", ["bear.bmp"], {}),
    ("Ntone", "make_n_tone", ["flower.bmp"], {"extra": "10"}),
    ("Saturate", "saturate", ["flower.bmp"], {}),
    ("TwoToneBetter", "make_better_two_tone", ["neptune.bmp"], {}),
    ("Blend", "blend_other", ["bear.bmp", "coral.bmp"], {}),
    ("BlendDiffSize", "blend_other", ["bear.bmp", "dog.bmp"], {}),
    ("BlendPercent", "blend_other", ["bear.bmp", "coral.bmp"], {"extra": "0.2"}),
    ("Chroma", "chroma_overlay", ["underwater.bmp", "scuba.bmp"], {"color": (0, 255, 0)}),
    ("ChromaColor", "chroma_overlay", ["underwater.bmp", "scuba-magenta.bmp"], {"color": (255, 0, 255)}),
    ("ChromaOffset", "chroma_overlay_stamp", ["underwater.bmp", "scuba-small.bmp"], {"clicked_coordinate": (100, 30), "color": (0, 255, 0)}),
    ("ChromaTolerance", "chroma_overlay", ["underwater.bmp", "scuba.bmp"], {"color": (0, 255, 0), "extra": "2"}),
    ("FadeVerticalIn", "fade_in_vertical", ["flower.bmp"], {}),
    ("FadeVerticalInColor", "fade_in_vertical", ["flower.bmp"], {"color": (0, 255, 255)}),
    ("FadeVerticalOut", "fade_out_vertical", ["flower.bmp"], {}),
    ("FadeVerticalOutColor", "fade_out_vertical", ["flower.bmp"], {"color": (0, 255, 255)}),
    ("FadeHorizontalIn", "fade_in_horizontal", ["flower.bmp"], {}),
    ("FadeHorizontalInColor", "fade_in_horizontal", ["flower.bmp"], {"color": (0, 255, 255)}),
    ("FadeHorizontalOut", "fade_out_horizontal", ["flower.bmp"], {}),
    ("FadeHorizontalOutColor", "fade_out_horizontal", ["flower.bmp"], {"color": (0, 255, 255)}),
    ("BlendGradualVertical", "blend_gradual_vertical", ["bear.bmp", "coral.bmp"], {}),
    ("BlendGradualHorizontal", "blend_gradual_horizontal", ["bear.bmp", "coral.bmp"], {}),
    ("LineDrawing", "make_line_drawing", ["flower.bmp"], {"color": (100, 0, 100)}),
    ("LineDrawingTolerance", "make_line_drawing", ["flower.bmp"], {"color": (100, 0, 100), "extra": "2"}),
    ("MirrorHorizontalLeft", "mirror_left_horizontal", ["flower.bmp"], {}),
    ("MirrorHorizontalRight", "mirror_right_horizontal", ["flower.bmp"], {}),
    ("MirrorVerticalBottom", "mirror_bottom_vertical", ["flower.bmp"], {}),
    ("MirrorVerticalTop", "mirror_top_vertical", ["flower.bmp"], {}),
    ("Shrink", "shrink", ["flower.bmp"], {}),
    ("ShrinkBetter", "better_shrink", ["flower.bmp"], {}),
    ("Enlarge", "enlarge", ["flower.bmp"], {}),
    ("EnlargeBetter", "better_enlarge", ["flower.bmp"], {}),
    ("ResizeLarger", "resize", ["flower.bmp"], {"extra": "4"}),
    ("ResizeSmaller", "resize", ["flower.bmp"], {"extra": "0.2"}),
    ("Autostereogram", "make_autostereogram", ["depthBoxes.bmp", "patternDots.bmp"], {}),
]

if __name__ == "__main__":
    student_folders = [
        # "/path/to/shared/student1/folder",
        # "/path/to/shared/student2/folder",
        # ...
    ]

    for student_folder in student_folders:
        student_name = student_folder.split("/")[-2]
        print("Testing " + student_name)
        tests.reverse()
        for test in tests:
            test_name = test[0]
            test_function_name = test[1]
            test_parameters = test[3]
            if "color" not in test_parameters:
                test_parameters["color"] = (255, 255, 255)
            if "extra" not in test_parameters:
                test_parameters["extra"] = "extra parameters..."

            spec = importlib.util.spec_from_file_location("ImageManip", student_folder + "/ImageManip.py")
            manip_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(manip_module)
            sol_spec = importlib.util.spec_from_file_location("ImageManipSolution", "ImageManip.py")
            sol_manip_module = importlib.util.module_from_spec(sol_spec)
            sol_spec.loader.exec_module(sol_manip_module)
            if test_function_name in dir(manip_module):
                test_function = getattr(manip_module, test_function_name)
                sol_function = getattr(sol_manip_module, test_function_name)
                if sol_function.__type__ == "tool":
                    if "clicked_coordinate" not in test_parameters:
                        test_parameters["clicked_coordinate"] = (20, 30)

                # if len(inspect.getfullargspec(test_function).args) >= len(test[3]) + len(test_parameters):
                print("Testing: " + test_name)
                with tempfile.NamedTemporaryFile(
                    suffix=".bmp", prefix=test_name + "_" + student_name, delete=False
                ) as student_image_file, tempfile.NamedTemporaryFile(suffix=".bmp", prefix=test_name + "_solution", delete=False) as solution_image_file, open(
                    os.path.join("images", test[2][0]), "rb"
                ) as file0:
                    file0.seek(0)
                    shutil.copyfileobj(file0, student_image_file)
                    file0.seek(0)
                    shutil.copyfileobj(file0, solution_image_file)
                    test_images = [student_image_file]
                    solution_images = [solution_image_file]
                    for file_name in test[2][1:]:
                        with open(os.path.join("images", file_name), "rb") as file_orig:
                            temp_file1 = tempfile.NamedTemporaryFile(delete=False)
                            file_orig.seek(0)
                            shutil.copyfileobj(file_orig, temp_file1)
                            test_images.append(temp_file1)
                            temp_file2 = tempfile.NamedTemporaryFile(delete=False)
                            file_orig.seek(0)
                            shutil.copyfileobj(file_orig, temp_file2)
                            solution_images.append(temp_file2)
                    try:
                        with tempfile.NamedTemporaryFile(
                            suffix=".bmp", prefix=test_name + "_" + student_name, delete=False
                        ) as student_result_image_file, tempfile.NamedTemporaryFile(
                            suffix=".bmp", prefix=test_name + "_solution", delete=False
                        ) as solution_result_image_file:
                            student_results = test_function(*test_images, **test_parameters)
                            if student_results is None:
                                student_results = test_images[0]
                            else:
                                student_results.seek(0)
                                shutil.copyfileobj(student_results, student_result_image_file)
                                student_results = student_result_image_file
                            student_results.flush()
                            solution_results = sol_function(*solution_images, **test_parameters)
                            if solution_results is None:
                                solution_results = solution_images[0]
                            else:
                                solution_results.seek(0)
                                shutil.copyfileobj(solution_results, solution_result_image_file)
                                solution_results = solution_result_image_file
                            solution_results.flush()
                            subprocess.run(["open", "-a", "Preview", student_results.name, solution_results.name], check=True)
                    except Exception as e:
                        print("Failed: " + str(e))
                        traceback.print_exc()
            else:
                print("Skipping: " + test_name)
