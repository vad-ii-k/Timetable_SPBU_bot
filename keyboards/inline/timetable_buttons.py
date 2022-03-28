from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date, timedelta

from keyboards.inline.callback_data import timetable_callback


async def create_timetable_keyboard(user_type: str, tt_id: int, day_counter=0) -> InlineKeyboardMarkup:
    if day_counter > 0:
        current_date = date.today() + timedelta(day_counter)
    else:
        current_date = date.today() - timedelta(-day_counter)
    prev_day_date = current_date - timedelta(days=1)
    next_day_date = current_date + timedelta(days=1)

    timetable_keyboard = InlineKeyboardMarkup()
    prev_day_button = InlineKeyboardButton(text="⬅ " + prev_day_date.strftime("%d.%m"),
                                           callback_data=timetable_callback.new(button="1-1",
                                                                                type=user_type,
                                                                                Id=tt_id))
    today_button = InlineKeyboardButton(text="—Сегодня—",
                                        callback_data=timetable_callback.new(button="1-2",
                                                                             type=user_type,
                                                                             Id=tt_id))
    next_day_button = InlineKeyboardButton(text=next_day_date.strftime("%d.%m") + " ➡️",
                                           callback_data=timetable_callback.new(button="1-3",
                                                                                type=user_type,
                                                                                Id=tt_id))
    timetable_keyboard.row(prev_day_button, today_button, next_day_button)

    this_week_button = InlineKeyboardButton(text="⏹ Эта неделя",
                                            callback_data=timetable_callback.new(button="2-1",
                                                                                 type=user_type,
                                                                                 Id=tt_id))
    next_week_button = InlineKeyboardButton(text="След. неделя ⏩",
                                            callback_data=timetable_callback.new(button="2-2",
                                                                                 type=user_type,
                                                                                 Id=tt_id))
    timetable_keyboard.row(this_week_button, next_week_button)
    picture_button = InlineKeyboardButton(text="🖼 Картинкой 🖼",
                                   callback_data=timetable_callback.new(button="3-1",
                                                                        type='picture',
                                                                        Id=0))
    timetable_keyboard.row(picture_button)

    return timetable_keyboard
