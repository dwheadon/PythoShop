import importlib.util
import math
import os
import time
import typing
from io import BytesIO

from kivy.app import App
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.input.providers.mouse import MouseMotionEvent
from kivy.uix.button import Button
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image as UixImage
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from PIL import Image

from ImageManip import *
from tests.config import DEFAULT_STARTING_PRIMARY_IMAGE_PATH, DEFAULT_STARTING_SECONDARY_IMAGE_PATH


class NoImageError(Exception):
    pass


class ImageDisplay:
    def __init__(self, *, is_primary: bool) -> None:
        self.is_primary = is_primary
        self.uix_image: typing.Optional[UixImage] = None
        self.bytes: typing.Optional[BytesIO] = None

    def is_image_loaded(self) -> bool:
        return bool(self.uix_image)

    def load_image(self, uix_image: UixImage, bytes_: BytesIO) -> None:
        self.uix_image = uix_image
        self.bytes = bytes_

    def get_scatter(self) -> typing.Any:
        if self.is_primary:
            return PythoShopApp._root.image1
        else:
            return PythoShopApp._root.image2

    def do_binds(self) -> None:
        assert self.uix_image

        self.uix_image.texture = CoreImage(self.bytes, ext="bmp").texture
        # to avoid anti-aliassing when zoomed
        self.uix_image.texture.mag_filter = "nearest"
        self.uix_image.texture.min_filter = "nearest"

    def do_resize(self) -> None:
        assert self.uix_image
        self.uix_image.size_hint = [None, None]

        # Callback to change size of image based on the rendered scatter
        def resize_image(instance, value):
            assert self.uix_image
            self.uix_image.size = instance.size
            self.uix_image.pos = (0, 0)

        # Bind resize_image to size and pos changes of the scatter
        # NB: This is required since at the start of the program we don't
        # yet know the final size of the scatter.
        scatter = self.get_scatter()
        scatter.bind(size=resize_image, pos=resize_image)
        scatter.add_widget(self.uix_image, 100)

        self.uix_image.size = scatter.size
        self.uix_image.pos = (0, 0)


def _set_extra(value: str) -> None:
    """
    Set the "extra parameters..." box to a particular value

    :params value: The value to put in the box
    :returns: None
    """
    PythoShopApp._root.extra_input.text = value


def _select_coordinate(x: int, y: int) -> None:
    """
    Put a given (x, y) coordinate into the `extra parameters...` box

    :param x: x value coordinate to set the system to
    :param y: y value coordinate to set the system to
    :returns: None
    """
    _set_extra(f"{x}, {y}")


def _is_primary_tab_selected() -> bool:
    """
    Determine if the "primary" tab is selected in the Kivy window.

    :returns: T/F if primary tab is selected
    """
    return bool(PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.primary_tab)


def _is_secondary_tab_selected() -> bool:
    """
    Determine if the "secondary" tab is selected in the Kivy window.

    :returns: T/F if secondary tab is selected
    """
    return bool(PythoShopApp._root.images_panel.current_tab == PythoShopApp._root.secondary_tab)


def _get_current_image() -> ImageDisplay:
    """
    Get the data associated with the currently loaded image

    :returns: Tuple of (image, bytes_in_image, and image_scatter)
    """
    if _is_primary_tab_selected():
        return PythoShopApp._image1
    elif _is_secondary_tab_selected():
        return PythoShopApp._image2
    else:
        raise NoImageError("Neither image tab was selected (which shouldn't be possible)")


def _select_color(x: int, y: int) -> None:  # sourcery skip: merge-else-if-into-elif
    """
    Set the color picker to be the RGB of a particular (x, y) coordinate

    :param x: The x value of the pixel to sample
    :param y: The y value of the pixel to sample
    :returns: None
    """
    assert PythoShopApp._color_picker

    image = _get_current_image()
    if image.bytes:
        img = Image.open(image.bytes)
        r, g, b = img.getpixel((x, img.height - 1 - y))
        PythoShopApp._color_picker.color = (r / 255, g / 255, b / 255, 1)


def _get_image_bytes(file_name: str) -> BytesIO:
    if os.path.splitext(file_name)[-1].lower() == ".bmp":
        # Load it directly rather than going through Pillow where we might loose some fidelity (e.g. paddding bytes)
        current_bytes = BytesIO()
        current_bytes.write(open(file_name, "rb").read())
    else:
        current_bytes = BytesIO()
        img = Image.open(file_name)
        img = img.convert("RGB")
        img.save(current_bytes, format="bmp")
        img.close()

    return current_bytes


def _get_chosen_color() -> tuple[int, int, int]:
    """
    Get currently selected color in RGB format

    :returns: RBG tuple
    """
    return (
        int(PythoShopApp._root.color_button.background_color[0] * 255),
        int(PythoShopApp._root.color_button.background_color[1] * 255),
        int(PythoShopApp._root.color_button.background_color[2] * 255),
    )


def _get_extra_text() -> str:
    """
    Get text in the "extra parameters..." box

    :returns: String that is inside the box
    """
    return PythoShopApp._root.extra_input.text


def _is_touch_in_image(cimage: UixImage, event: MouseMotionEvent, cscatter) -> bool:
    if not cimage.parent.collide_point(*event.pos):
        return False
    else:
        lr_space = (cimage.width - cimage.norm_image_size[0]) / 2  # empty space in Image widget left and right of actual image
        tb_space = (cimage.height - cimage.norm_image_size[1]) / 2  # empty space in Image widget above and below actual image
        pixel_x = event.x - lr_space - cscatter.x  # x coordinate of touch measured from lower left of actual image
        pixel_y = event.y - tb_space - cscatter.y  # y coordinate of touch measured from lower left of actual image
        if pixel_x < 0 or pixel_y < 0:
            return False
        elif pixel_x >= cimage.norm_image_size[0] or pixel_y >= cimage.norm_image_size[1]:
            return False
        else:
            return True


def _handle_touch_in_image(cimage: UixImage, event: MouseMotionEvent, cscatter) -> None:
    lr_space = (cimage.width - cimage.norm_image_size[0]) / 2  # empty space in Image widget left and right of actual image
    tb_space = (cimage.height - cimage.norm_image_size[1]) / 2  # empty space in Image widget above and below actual image
    pixel_x = event.x - lr_space - cscatter.x  # x coordinate of touch measured from lower left of actual image
    pixel_y = event.y - tb_space - cscatter.y  # y coordinate of touch measured from lower left of actual image

    assert pixel_x >= 0 and pixel_y >= 0 and pixel_x < cimage.norm_image_size[0] and pixel_y < cimage.norm_image_size[1]

    # scale coordinates to actual pixels of the Image source
    actual_x = int(pixel_x * cimage.texture_size[0] / cimage.norm_image_size[0])
    actual_y = int(pixel_y * cimage.texture_size[1] / cimage.norm_image_size[1])

    # Note: can't call your manip functions "_select_"
    if PythoShopApp._tool_function.__name__[:8] == "_select_":
        PythoShopApp._tool_function(actual_x, actual_y)
    else:
        run_manip_function(PythoShopApp._tool_function, clicked_coordinate=(actual_x, actual_y))


def _write_image_to_file_system(bytes: BytesIO) -> None:
    """
    Writes given bytes to the file system as a bitmap

    :param bytes: Bytes of bitmap to write to the filesystem
    :returns: None
    """
    bytes.seek(0)
    new_image_file_name = os.path.join(os.path.expanduser("~"), "Desktop", "PythoShop " + time.strftime("%Y-%m-%d at %H.%M.%S") + ".bmp")
    new_image_file = open(new_image_file_name, "wb")
    new_image_file.write(bytes.read())
    new_image_file.close()


def _check_bmp_integrity(image: BytesIO) -> None:
    """
    Check (assert) that all the properties of a BitMap image are correct

    :param image: Image to assert is a proper bitmap
    :returns: None
    """
    image.seek(0)
    assert image.read(2) == b"\x42\x4D", "header field was invalid"
    file_byte_size = int.from_bytes(image.read(4), "little")

    image.seek(10)
    first_pixel_offset = int.from_bytes(image.read(4), "little")
    header_size = int.from_bytes(image.read(4), "little")  # should be fpp - 14
    pixel_width = int.from_bytes(image.read(4), "little")
    pixel_height = int.from_bytes(image.read(4), "little")
    color_planes = int.from_bytes(image.read(2), "little")
    assert color_planes == 1, "color planes should be 1"
    bits_per_pixel = int.from_bytes(image.read(2), "little")

    bits_per_pixel_possibilities = [1, 4, 8, 16, 24, 32]
    assert bits_per_pixel in bits_per_pixel_possibilities, (
        "bits per pixel is set to " + str(bits_per_pixel) + " which is not one of the allowed options: " + ", ".join(bits_per_pixel_possibilities)
    )
    bits_per_row = pixel_width * bits_per_pixel
    bytes_per_row = math.ceil(bits_per_row / 8)
    padding_bytes = 0
    if bytes_per_row % 4 != 0:
        padding_bytes = 4 - bytes_per_row % 4
    row_byte_size = bytes_per_row + padding_bytes
    theoretical_file_size = first_pixel_offset + row_byte_size * pixel_height
    assert file_byte_size == theoretical_file_size, "file size is incorrect"

    compression = int.from_bytes(image.read(4), "little")
    assert compression == 0, "PythoShop doesn't support images with compression"
    pixel_data_byte_size = int.from_bytes(image.read(4), "little")
    assert pixel_data_byte_size == 0 or pixel_data_byte_size == row_byte_size * pixel_height, "pixel data size can either be 0 or the actual size"
    # only validates the header up to position 38
    image.seek(0)


def run_manip_function(func: typing.Callable, **kwargs) -> None:
    if _is_primary_tab_selected():
        image1 = PythoShopApp._image1
        image2 = PythoShopApp._image2
    elif _is_secondary_tab_selected():
        image1 = PythoShopApp._image2
        image2 = PythoShopApp._image1
    else:
        raise NoImageError("Neither image tab was selected (which shouldn't be possible)")

    if not image1.uix_image or not image1.bytes:
        raise NoImageError("The currently selected tab doesn't have an image loaded into it")

    try:
        image1.bytes.seek(0)
        kwargs["color"] = _get_chosen_color()
        kwargs["extra"] = _get_extra_text()
        if image2.bytes:
            image2.bytes.seek(0)
            kwargs["other_image"] = image2.bytes

        result = func(image1.bytes, **kwargs)
        if result != None:  # Something was returned, make sure it was an image file
            if result.__class__ != BytesIO:
                raise Exception("Function", func.__name__, "should have returned an image but instead returned something else")
            verified_bytes = result
        else:  # No return: assume that the change has been made to the image itself (img1)
            verified_bytes = image1.bytes

        try:
            _check_bmp_integrity(verified_bytes)
        except AssertionError as ae:
            raise Exception('The image returned by "' + func.__name__ + '" was corrupt and cannot be displayed: ' + str(ae))

        verified_bytes.seek(0)
        image1.load_image(image1.uix_image, verified_bytes)
        image1.do_binds()
    except SyntaxError:
        print("Error: ", func.__name__, "generated an exception")


class FileChooserDialog(Widget):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        if "rootpath" in kwargs:
            self.file_chooser.rootpath = kwargs["rootpath"]

    def open(self, file_name: list[str]) -> None:
        if len(file_name) != 1:
            return

        image = _get_current_image()

        scatter = image.get_scatter()
        if image.uix_image:
            scatter.remove_widget(image.uix_image)

        PhotoShopWidget._file_chooser_popup.dismiss()

        current_bytes = _get_image_bytes(file_name[0])
        current_bytes.seek(0)

        uix_image = UixImage(fit_mode="contain")
        image.load_image(uix_image, current_bytes)
        image.do_binds()
        image.do_resize()


class PhotoShopWidget(Widget):
    _file_chooser_popup = None

    def toggle_color(self) -> None:
        if PythoShopApp._color_picker.is_visible:
            PythoShopApp._root.children[0].remove_widget(PythoShopApp._color_picker)
            PythoShopApp._color_picker.is_visible = False
            PythoShopApp._root.color_button.text = "Change Color"
        else:
            PythoShopApp._root.children[0].add_widget(PythoShopApp._color_picker)
            PythoShopApp._color_picker.is_visible = True
            PythoShopApp._root.color_button.text = "Set Color"

    def load_image(self) -> None:
        if not PhotoShopWidget._file_chooser_popup:
            PhotoShopWidget._file_chooser_popup = Popup(title="Choose an image", content=FileChooserDialog(rootpath=os.path.expanduser("~")))
        PhotoShopWidget._file_chooser_popup.open()

    def save_image(self) -> None:
        image = _get_current_image()
        if image.bytes:
            _write_image_to_file_system(image.bytes)

    def apply_tool(self, event: MouseMotionEvent, callback: typing.Callable) -> bool:
        image = _get_current_image()

        uix_image = image.uix_image
        scatter = image.get_scatter()
        if uix_image and PythoShopApp._tool_function and _is_touch_in_image(uix_image, event, scatter):
            _handle_touch_in_image(uix_image, event, scatter)
            return True
        else:
            return callback(event)

    def on_touch_down(self, touch: MouseMotionEvent) -> None:
        self.apply_tool(touch, super().on_touch_down)

    def on_touch_move(self, movement: MouseMotionEvent) -> None:
        self.apply_tool(movement, super().on_touch_move)


class PythoShopApp(App):
    _image1: ImageDisplay = ImageDisplay(is_primary=True)
    _image2: ImageDisplay = ImageDisplay(is_primary=False)
    _root: typing.Any = None
    _tool_function: typing.Any = None
    _color_picker: typing.Optional[ColorPicker] = None
    _first_color = True

    def on_color(self, value: list[int]) -> None:
        """
        Callback method to retrieve colors for kivy's ColorPicker object

        :param value: The color currently selected in rgba format
        :returns: None
        """
        my_value = value.copy()  # we ignore the alpha chanel
        my_value[3] = 1
        PythoShopApp._root.color_button.background_normal = ""
        PythoShopApp._root.color_button.background_color = my_value
        if (value[0] + value[1] + value[2]) * value[3] > 1.5:
            PythoShopApp._root.color_button.color = [0, 0, 0, 1]
        else:
            PythoShopApp._root.color_button.color = [1, 1, 1, 1]

        if not PythoShopApp._first_color:
            PythoShopApp._root.color_button.text = "Set Color"
        else:
            PythoShopApp._first_color = False

    def _on_file_drop(self, window, file_path: str) -> None:
        PythoShopApp._root.extra_input.text = file_path

    def build(self) -> None:
        Window.bind(on_dropfile=self._on_file_drop)
        PythoShopApp._root = PhotoShopWidget()
        # Find the functions that can be run
        try:
            PythoShopApp._filter_dropdown = DropDown()
            PythoShopApp._tool_dropdown = DropDown()
            PythoShopApp._color_dropdown = DropDown()
            PythoShopApp._color_picker = ColorPicker()
            PythoShopApp._color_picker.children[0].children[1].children[4].disabled = True  # disable the alpha chanel
            PythoShopApp._color_picker.bind(color=PythoShopApp.on_color)
            PythoShopApp._color_picker.is_visible = False

            # Selection tools come first
            select_coord_button = Button(text="Select coordinate", size_hint_y=None, height=44)
            select_coord_button.func = _select_coordinate
            select_coord_button.bind(on_release=lambda btn: PythoShopApp._tool_dropdown.select(btn))
            PythoShopApp._tool_dropdown.add_widget(select_coord_button)
            select_color_button = Button(text="Select color", size_hint_y=None, height=44)
            select_color_button.func = _select_color
            select_color_button.bind(on_release=lambda btn: PythoShopApp._tool_dropdown.select(btn))
            PythoShopApp._tool_dropdown.add_widget(select_color_button)

            spec = importlib.util.spec_from_file_location("ImageManip", os.getcwd() + "/ImageManip.py")
            manip_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(manip_module)  # try to load it to see if we have a syntax error
            for attribute in dir(manip_module):
                thing = getattr(manip_module, attribute)
                if callable(thing) and hasattr(thing, "__wrapped__") and hasattr(thing, "__type__"):
                    if getattr(thing, "__type__") == "filter":
                        btn = Button(text=attribute, size_hint_y=None, height=44)
                        btn.func = thing
                        btn.bind(on_release=lambda btn: PythoShopApp._filter_dropdown.select(btn))
                        PythoShopApp._filter_dropdown.add_widget(btn)
                    elif getattr(thing, "__type__") == "tool":
                        btn = Button(text=attribute, size_hint_y=None, height=44)
                        btn.func = thing
                        btn.bind(on_release=lambda btn: PythoShopApp._tool_dropdown.select(btn))
                        PythoShopApp._tool_dropdown.add_widget(btn)
                    else:
                        print("Error: unrecognized manipulation")
            PythoShopApp._root.filter_button.bind(on_release=PythoShopApp._filter_dropdown.open)
            PythoShopApp._root.tool_button.bind(on_release=PythoShopApp._tool_dropdown.open)

            def select_filter(self, btn):
                # currently selected tab actually has an image
                image = _get_current_image()
                if image.is_image_loaded():
                    run_manip_function(btn.func)

            PythoShopApp._filter_dropdown.bind(on_select=select_filter)

            def select_tool(self, btn):
                setattr(PythoShopApp._root.tool_button, "text", btn.text)
                PythoShopApp._tool_function = btn.func

            PythoShopApp._tool_dropdown.bind(on_select=select_tool)
        except SyntaxError:
            print("Error: ImageManip.py has a syntax error and can't be executed")

        if os.path.exists(DEFAULT_STARTING_PRIMARY_IMAGE_PATH):
            current_bytes = _get_image_bytes(DEFAULT_STARTING_PRIMARY_IMAGE_PATH)
            current_bytes.seek(0)

            # Create a Kivy Image widget for the loaded image
            uix_image = UixImage(fit_mode="contain")
            PythoShopApp._image1.load_image(uix_image, current_bytes)
            PythoShopApp._image1.do_binds()
            PythoShopApp._image1.do_resize()

        if os.path.exists(DEFAULT_STARTING_SECONDARY_IMAGE_PATH):
            current_bytes = _get_image_bytes(DEFAULT_STARTING_SECONDARY_IMAGE_PATH)
            current_bytes.seek(0)

            # Create a Kivy Image widget for the loaded image
            uix_image = UixImage(fit_mode="contain")
            PythoShopApp._image2.load_image(uix_image, current_bytes)
            PythoShopApp._image2.do_binds()
            PythoShopApp._image2.do_resize()

        return PythoShopApp._root


if __name__ == "__main__":
    PythoShopApp().run()
