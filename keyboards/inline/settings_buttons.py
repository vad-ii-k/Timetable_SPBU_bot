from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import settings_callback
from utils.db_api.database import Settings


async def create_settings_keyboard(settings: Settings) -> InlineKeyboardMarkup:
    settings_keyboard = InlineKeyboardMarkup(row_width=1)

    text = "Присылать сводку на день: "
    if settings.daily_summary is None:
        text += '❌'
    daily_summary = InlineKeyboardButton(text=text,
                                         callback_data=settings_callback.new(type='daily_summary'))
    settings_keyboard.insert(daily_summary)

    text = "Уведомлять о начале пары: "
    if settings.notification_of_lesson is None:
        text += '❌'
    notification_of_lesson = InlineKeyboardButton(text=text,
                                                  callback_data=settings_callback.new(type='notification_of_lesson'))
    settings_keyboard.insert(notification_of_lesson)

    text = "Вид расписания по умолчанию: "
    text += '🖼' if settings.schedule_view_is_picture else '📝'
    schedule_view = InlineKeyboardButton(text=text,
                                         callback_data=settings_callback.new(type='schedule_view'))
    settings_keyboard.insert(schedule_view)
    return settings_keyboard
