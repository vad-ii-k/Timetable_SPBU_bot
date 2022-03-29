from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import settings_callback


async def create_settings_keyboard() -> InlineKeyboardMarkup:
    settings_keyboard = InlineKeyboardMarkup(row_width=1)
    daily_summary = InlineKeyboardButton(text="Присылать сводку на день: " + '❌',
                                         callback_data=settings_callback.new(type='daily_summary'))
    settings_keyboard.insert(daily_summary)
    notification_of_lesson = InlineKeyboardButton(text="Уведомлять о начале пары: " + '❌',
                                                  callback_data=settings_callback.new(type='notification_of_lesson'))
    settings_keyboard.insert(notification_of_lesson)
    schedule_view = InlineKeyboardButton(text="Вид расписания по умолчанию: " + 'текст',
                                         callback_data=settings_callback.new(type='schedule_view'))
    settings_keyboard.insert(schedule_view)
    return settings_keyboard
