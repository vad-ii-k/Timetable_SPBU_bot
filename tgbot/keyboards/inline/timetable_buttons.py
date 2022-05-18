from datetime import date, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.inline.callback_data import timetable_callback


async def create_timetable_keyboard(is_picture: bool, day_counter: int = 0) -> InlineKeyboardMarkup:
    current_date = date.today() + timedelta(day_counter)
    prev_day_date = current_date - timedelta(days=1)
    next_day_date = current_date + timedelta(days=1)

    timetable_keyboard = InlineKeyboardMarkup()
    prev_day_button = InlineKeyboardButton(
        text=f"⬅ {prev_day_date:%d.%m}", callback_data=timetable_callback.new(button="1-1"),
    )
    today_button = InlineKeyboardButton(
        text="Сегодня", callback_data=timetable_callback.new(button="1-2")
    )
    next_day_button = InlineKeyboardButton(
        text=f"{next_day_date:%d.%m} ➡️", callback_data=timetable_callback.new(button="1-3"),
    )
    if day_counter > -7:
        timetable_keyboard.row(prev_day_button, today_button, next_day_button)
    else:
        timetable_keyboard.row(today_button, next_day_button)

    this_week_button = InlineKeyboardButton(
        text="⏹ Эта неделя", callback_data=timetable_callback.new(button="2-1")
    )
    next_week_button = InlineKeyboardButton(
        text="След. неделя ⏩", callback_data=timetable_callback.new(button="2-2")
    )
    timetable_keyboard.row(this_week_button, next_week_button)

    text = "📝 Текстом 📝" if is_picture else "🖼 Картинкой 🖼"
    schedule_view = InlineKeyboardButton(
        text=text, callback_data=timetable_callback.new(button="3-1")
    )
    timetable_keyboard.row(schedule_view)

    return timetable_keyboard
