import io

from PIL import Image
from aiogram.types import BufferedInputFile


def image_to_buffered_input_file(image: Image) -> BufferedInputFile:
    image = Image.open(r"data\output.png")
    image_byte_arr = io.BytesIO()
    image.save(image_byte_arr, format=image.format)
    image_byte_arr = image_byte_arr.getvalue()
    buffered_photo = BufferedInputFile(file=image_byte_arr, filename="output.png")
    return buffered_photo
