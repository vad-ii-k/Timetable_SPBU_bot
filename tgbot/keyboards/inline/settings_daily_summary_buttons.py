from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.inline.callback_data import settings_daily_summary_callback


async def create_daily_summary_keyboard(selected_option: datetime) -> InlineKeyboardMarkup:
    daily_summary_keyboard = InlineKeyboardMarkup(row_width=2)

    suggested_time = [(19, "🕖"), (7, "🕖"), (20, "🕗"), (8, "🕗"), (21, "🕘"), (9, "🕘")]
    for option, sticker in suggested_time:
        button_time = InlineKeyboardButton(
            text=f"{'●' if selected_option is not None and option == selected_option.hour else '○'}"
                 f" {option}:00 {sticker}",
            callback_data=settings_daily_summary_callback.new(choice=option),
        )
        daily_summary_keyboard.insert(button_time)

    button_disabling = InlineKeyboardButton(
        text=("●" if (selected_option is None) else "○") + " Не присылать 🔇",
        callback_data=settings_daily_summary_callback.new(choice="disabling"),
    )
    daily_summary_keyboard.row(button_disabling)

    button_back = InlineKeyboardButton(
        text="Назад ↩️",
        callback_data=settings_daily_summary_callback.new(choice="back"),
    )
    daily_summary_keyboard.row(button_back)

    return daily_summary_keyboard
