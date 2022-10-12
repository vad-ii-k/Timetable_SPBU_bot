import io
import logging
import os

from pyppeteer import launch
from PIL import Image
from jinja2 import Environment, FileSystemLoader
from aiogram.types import BufferedInputFile

from tgbot.data_classes import Schedule


async def take_browser_screenshot(schedule: Schedule):
    results_filename = r"data/compiled_html_pages/schedule.html"
    environment = Environment(loader=FileSystemLoader(r"data/html_templates"))
    results_template = environment.get_template(r"schedule.html")

    with open(results_filename, mode="w", encoding="utf-8") as results:
        results.write(results_template.render(schedule=schedule))

    browser = await launch(
        defaultViewport={'width': 3000, 'height': 3000},
        logLevel=logging.ERROR,
        headless=True,
        executablePath="/usr/bin/chromium-browser",
        args=['--no-sandbox']
    )
    page_for_psv = await browser.newPage()
    await page_for_psv.goto(f'file:///{os.path.abspath("data/compiled_html_pages/schedule.html")}')
    await page_for_psv.screenshot(path='data/output.png', type='jpeg', fullPage=True, quality=90)
    await browser.close()


async def image_to_buffered_input_file(schedule: Schedule) -> BufferedInputFile:
    await take_browser_screenshot(schedule)
    image = Image.open(r"data/output.png")
    image_byte_arr = io.BytesIO()
    image.save(image_byte_arr, format=image.format)
    image_byte_arr = image_byte_arr.getvalue()
    buffered_photo = BufferedInputFile(file=image_byte_arr, filename="output.png")
    return buffered_photo
