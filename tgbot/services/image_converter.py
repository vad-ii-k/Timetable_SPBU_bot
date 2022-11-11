""" Module for converting a schedule into an image """
import logging
import os
from datetime import timedelta, date
from itertools import groupby
from typing import Literal

from aiogram.types import BufferedInputFile
from babel.dates import format_date
from jinja2 import Environment, FileSystemLoader
from pyppeteer import launch, connect

from tgbot.services.schedule.class_schedule import Schedule, StudyEvent


_WS_ENDPOINT: str | None = None


async def get_dates_of_days_of_week(schedule: Schedule) -> list[date]:
    """

    :param schedule:
    :return:
    """
    from_date, to_date = schedule.from_date, schedule.to_date
    dates_of_days_of_week = [from_date + timedelta(days=index) for index in range((to_date - from_date).days)]
    return dates_of_days_of_week


async def render_template(schedule: Schedule, schedule_type: Literal['day', 'week']) -> None:
    """

    :param schedule:
    :param schedule_type:
    :return:
    """
    result_path = f"data/compiled_html_pages/{schedule_type}_schedule.html"
    environment = Environment(loader=FileSystemLoader("data/html_templates"))

    def date_format_ru(value):
        """

        :param value:
        :return:
        """
        return format_date(value, "EEEE, d MMM", locale='ru')

    environment.filters["date_format_ru"] = date_format_ru

    def events_group_by(events: list[StudyEvent], key_type: Literal['time', 'event_info']):
        """

        :param events:
        :param key_type:
        :return:
        """
        def key_func_event_info(event: StudyEvent):
            """

            :param event:
            :return:
            """
            return event.name, event.event_format, event.is_canceled

        def key_func_time(event: StudyEvent):
            """

            :param event:
            :return:
            """
            return event.start_time, event.end_time

        return groupby(events, key=key_func_time if key_type == 'time' else key_func_event_info)

    environment.filters["events_group_by"] = events_group_by

    results_template = environment.get_template(f"{schedule_type}_schedule.html")

    with open(file=result_path, mode="w", encoding="utf-8") as result:
        result.write(results_template.render(
            schedule=schedule,
            dates_of_days_of_week=await get_dates_of_days_of_week(schedule),
            dates_of_event_days=list(map(lambda e: e.day, schedule.events_days))
        ))


async def take_browser_screenshot(schedule_type: Literal['day', 'week']):
    """

    :param schedule_type:
    """
    default_viewport = {'width': 2048 if schedule_type == 'week' else 1408, 'height': 256}
    global _WS_ENDPOINT
    if _WS_ENDPOINT:
        browser = await connect(browserWSEndpoint=_WS_ENDPOINT, defaultViewport=default_viewport)
    else:
        browser = await launch(
            defaultViewport=default_viewport,
            logLevel=logging.ERROR,
            headless=True,
            executablePath="/usr/bin/chromium-browser",
            args=['--no-sandbox']
        )
        _WS_ENDPOINT = browser.wsEndpoint
    browser_page = await browser.newPage()
    await browser_page.goto(f'file:///{os.path.abspath(f"data/compiled_html_pages/{schedule_type}_schedule.html")}')
    await browser_page.screenshot(path='data/output.jpeg', type='jpeg', fullPage=True, quality=99)
    await browser_page.close()


async def get_rendered_image(schedule: Schedule, schedule_type: Literal['day', 'week']) -> BufferedInputFile:
    """

    :param schedule:
    :param schedule_type:
    :return:
    """
    await render_template(schedule, schedule_type)
    await take_browser_screenshot(schedule_type)
    file_name = f"{schedule.from_date:%d.%m}-{schedule.to_date:%d.%m}.jpg"
    photo = BufferedInputFile.from_file(r"data/output.jpeg", filename=file_name)
    return photo
