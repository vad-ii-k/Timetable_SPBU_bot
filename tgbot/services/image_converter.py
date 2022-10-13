import logging
import os
from typing import Literal

from pyppeteer import launch
from jinja2 import Environment, FileSystemLoader
from aiogram.types import BufferedInputFile

from tgbot.data_classes import Schedule


async def render_template(schedule: Schedule, schedule_type: Literal['day', 'week']):
    result_path = f"data/compiled_html_pages/{schedule_type}_schedule.html"
    environment = Environment(loader=FileSystemLoader("data/html_templates"))
    results_template = environment.get_template(f"{schedule_type}_schedule.html")

    with open(file=result_path, mode="w", encoding="utf-8") as result:
        result.write(results_template.render(schedule=schedule))


async def take_browser_screenshot(schedule_type: Literal['day', 'week']):
    browser = await launch(
        defaultViewport={'width': 2048, 'height': 2048},
        logLevel=logging.ERROR,
        headless=True,
        executablePath="/usr/bin/chromium-browser",
        args=['--no-sandbox']
    )
    browser_page = await browser.newPage()
    await browser_page.goto(f'file:///{os.path.abspath(f"data/compiled_html_pages/{schedule_type}_schedule.html")}')
    await browser_page.screenshot(path='data/output.jpeg', type='jpeg', fullPage=True, quality=90)
    await browser.close()


async def get_rendered_image(schedule: Schedule, schedule_type: Literal['day', 'week']) -> BufferedInputFile:
    await render_template(schedule, schedule_type)
    await take_browser_screenshot(schedule_type)
    file_name = f"{schedule.from_date:%d.%m}-{schedule.to_date:%d.%m}.jpg"
    photo = BufferedInputFile.from_file(r"data/output.jpeg", filename=file_name)
    return photo
