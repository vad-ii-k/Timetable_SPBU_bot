import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.inline.callback_data import settings_callback
from utils.db_api.db_commands import Settings


async def create_settings_keyboard(settings: Settings) -> InlineKeyboardMarkup:
    settings_keyboard = InlineKeyboardMarkup(row_width=1)

    text = "Присылать сводку "
    if settings.daily_summary is None:
        text += 'на день: ❌'
    else:
        if settings.daily_summary > datetime.time(12):
            text += 'за день до: в '
        else:
            text += 'день в день: в '
        text += settings.daily_summary.strftime('%H:%M')
    daily_summary = InlineKeyboardButton(text=text,
                                         callback_data=settings_callback.new(type='daily_summary'))
    settings_keyboard.insert(daily_summary)

    text = "Уведомлять о начале пары: "
    if settings.notification_of_lesson is None:
        text += '❌'
    notification_of_lesson = InlineKeyboardButton(text=text,
                                                  callback_data=settings_callback.new(type='notification_of_lesson'))
    # settings_keyboard.insert(notification_of_lesson)

    text = "Вид расписания по умолчанию: "
    text += '🖼' if settings.schedule_view_is_picture else '📝'
    schedule_view = InlineKeyboardButton(text=text,
                                         callback_data=settings_callback.new(type='schedule_view'))
    settings_keyboard.insert(schedule_view)
    return settings_keyboard
