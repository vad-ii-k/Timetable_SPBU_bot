from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.inline.callback_data import schedule_subscription_callback


async def create_schedule_subscription_keyboard() -> InlineKeyboardMarkup:
    schedule_subscription_keyboard = InlineKeyboardMarkup(row_width=1)

    yes_button = InlineKeyboardButton(
        text="Да, сделать основным ✅",
        callback_data=schedule_subscription_callback.new(answer=1),
    )
    schedule_subscription_keyboard.insert(yes_button)

    no_button = InlineKeyboardButton(
        text="Нет, только посмотреть ❌",
        callback_data=schedule_subscription_callback.new(answer=0),
    )
    schedule_subscription_keyboard.insert(no_button)

    return schedule_subscription_keyboard
