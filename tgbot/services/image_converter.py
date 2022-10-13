import logging
import os

from pyppeteer import launch
from jinja2 import Environment, FileSystemLoader
from aiogram.types import BufferedInputFile

from tgbot.data_classes import Schedule


async def render_template(schedule: Schedule):
    results_filename = r"data/compiled_html_pages/schedule.html"
    environment = Environment(loader=FileSystemLoader(r"data/html_templates"))
    results_template = environment.get_template(r"schedule.html")

    with open(results_filename, mode="w", encoding="utf-8") as results:
        results.write(results_template.render(schedule=schedule))


async def take_browser_screenshot():
    browser = await launch(
        defaultViewport={'width': 2048, 'height': 2048},
        logLevel=logging.ERROR,
        headless=True,
        executablePath="/usr/bin/chromium-browser",
        args=['--no-sandbox']
    )
    page_for_psv = await browser.newPage()
    await page_for_psv.goto(f'file:///{os.path.abspath("data/compiled_html_pages/schedule.html")}')
    await page_for_psv.screenshot(path='data/output.jpeg', type='jpeg', fullPage=True, quality=90)
    await browser.close()


async def get_rendered_image(schedule: Schedule) -> BufferedInputFile:
    await render_template(schedule)
    await take_browser_screenshot()
    file_name = f"{schedule.from_date:%d.%m}-{schedule.to_date:%d.%m}.jpg"
    photo = BufferedInputFile.from_file(r"data/output.jpeg", filename=file_name)
    return photo
