from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.inline.callback_data import settings_daily_summary_callback


async def create_daily_summary_keyboard(selected_option: datetime) -> InlineKeyboardMarkup:
    daily_summary_keyboard = InlineKeyboardMarkup(row_width=2)

    suggested_time = [(19, "π"), (7, "π"), (20, "π"), (8, "π"), (21, "π"), (9, "π")]
    for option, sticker in suggested_time:
        button_time = InlineKeyboardButton(
            text=f"{'β' if selected_option is not None and option == selected_option.hour else 'β'}"
                 f" {option}:00 {sticker}",
            callback_data=settings_daily_summary_callback.new(choice=option),
        )
        daily_summary_keyboard.insert(button_time)

    button_disabling = InlineKeyboardButton(
        text=("β" if (selected_option is None) else "β") + " ΠΠ΅ ΠΏΡΠΈΡΡΠ»Π°ΡΡ π",
        callback_data=settings_daily_summary_callback.new(choice="disabling"),
    )
    daily_summary_keyboard.row(button_disabling)

    button_back = InlineKeyboardButton(
        text="ΠΠ°Π·Π°Π΄ β©οΈ",
        callback_data=settings_daily_summary_callback.new(choice="back"),
    )
    daily_summary_keyboard.row(button_back)

    return daily_summary_keyboard
