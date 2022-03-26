from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date, timedelta

from keyboards.inline.callback_data import timetable_callback


async def create_timetable_keyboard(prev_day_date=date.today() - timedelta(days=1),
                                    next_day_date=date.today() + timedelta(days=1)):

    timetable_keyboard = InlineKeyboardMarkup()
    prev_day_button = InlineKeyboardButton(text="⬅ " + prev_day_date.strftime("%d.%m"),
                                           callback_data=timetable_callback.new(button="1-1"))
    today_button = InlineKeyboardButton(text="—Сегодня—",
                                        callback_data=timetable_callback.new(button="1-2"))
    next_day_button = InlineKeyboardButton(text=next_day_date.strftime("%d.%m") + " ➡️",
                                           callback_data=timetable_callback.new(button="1-3"))
    timetable_keyboard.row(prev_day_button, today_button, next_day_button)

    this_week_button = InlineKeyboardButton(text="⏹ Эта неделя",
                                            callback_data=timetable_callback.new(button="2-1"))
    next_week_button = InlineKeyboardButton(text="След. неделя ⏩",
                                            callback_data=timetable_callback.new(button="2-2"))
    timetable_keyboard.row(this_week_button, next_week_button)

    return timetable_keyboard
