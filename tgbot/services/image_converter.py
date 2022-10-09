import io

import imgkit
from PIL import Image
from jinja2 import Environment, FileSystemLoader
from aiogram.types import BufferedInputFile


async def image_to_buffered_input_file() -> BufferedInputFile:
    results_filename = r"data/compiled_html_pages/schedule.html"
    environment = Environment(loader=FileSystemLoader(r"data/html_templates"))
    results_template = environment.get_template(r"schedule.html")

    with open(results_filename, mode="w", encoding="utf-8") as results:
        results.write(results_template.render())

    imgkit.from_file(results_filename, 'data/output.png')

    image = Image.open(r"data/output.png")
    image_byte_arr = io.BytesIO()
    image.save(image_byte_arr, format=image.format)
    image_byte_arr = image_byte_arr.getvalue()
    buffered_photo = BufferedInputFile(file=image_byte_arr, filename="output.png")
    return buffered_photo
