import logging
import os
from datetime import timedelta, date
from typing import Literal

from babel.dates import format_date
from pyppeteer import launch
from jinja2 import Environment, FileSystemLoader
from aiogram.types import BufferedInputFile

from tgbot.services.schedule.class_schedule import Schedule


async def get_dates_of_days_of_week(schedule: Schedule) -> list[date]:
    from_date, to_date = schedule.from_date, schedule.to_date
    dates_of_days_of_week = [from_date + timedelta(days=index) for index in range((to_date - from_date).days)]
    return dates_of_days_of_week


async def render_template(schedule: Schedule, schedule_type: Literal['day', 'week']):
    result_path = f"data/compiled_html_pages/{schedule_type}_schedule.html"
    environment = Environment(loader=FileSystemLoader("data/html_templates"), enable_async=True)

    def date_format_ru(value):
        return format_date(value, "EEEE, d MMM", locale='ru')
    environment.filters["date_format_ru"] = date_format_ru

    results_template = environment.get_template(f"{schedule_type}_schedule.html")

    with open(file=result_path, mode="w", encoding="utf-8") as result:
        result.write(await results_template.render_async(
            schedule=schedule,
            dates_of_days_of_week=await get_dates_of_days_of_week(schedule),
            dates_of_event_days=list(map(lambda e: e.day, schedule.events_days))
        ))


async def take_browser_screenshot(schedule_type: Literal['day', 'week']):
    browser_width = 2048 if schedule_type == 'week' else 1536
    browser = await launch(
        defaultViewport={'width': browser_width, 'height': 256},
        logLevel=logging.ERROR,
        headless=True,
        executablePath="/usr/bin/chromium-browser",
        args=['--no-sandbox']
    )
    browser_page = await browser.newPage()
    await browser_page.goto(f'file:///{os.path.abspath(f"data/compiled_html_pages/{schedule_type}_schedule.html")}')
    await browser_page.screenshot(path='data/output.jpeg', type='jpeg', fullPage=True, quality=100)
    await browser.close()


async def get_rendered_image(schedule: Schedule, schedule_type: Literal['day', 'week']) -> BufferedInputFile:
    await render_template(schedule, schedule_type)
    await take_browser_screenshot(schedule_type)
    file_name = f"{schedule.from_date:%d.%m}-{schedule.to_date:%d.%m}.jpg"
    photo = BufferedInputFile.from_file(r"data/output.jpeg", filename=file_name)
    return photo
