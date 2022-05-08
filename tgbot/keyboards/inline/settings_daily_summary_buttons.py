from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.inline.callback_data import settings_daily_summary_callback
from utils.db_api.db_commands import Settings


async def create_daily_summary_keyboard(settings: Settings) -> InlineKeyboardMarkup:
    daily_summary_keyboard = InlineKeyboardMarkup()

    suggested_time = [7, 8, 9]
    for option in suggested_time:
        button_left = InlineKeyboardButton(text=str(option+12)+':00',
                                           callback_data=settings_daily_summary_callback.new(choice=option+12))
        button_right = InlineKeyboardButton(text=str(option) + ':00',
                                            callback_data=settings_daily_summary_callback.new(choice=option))
        daily_summary_keyboard.row(button_left, button_right)

    button_disabling = InlineKeyboardButton(text='Не присылать ❌',
                                            callback_data=settings_daily_summary_callback.new(choice='disabling'))
    daily_summary_keyboard.row(button_disabling)
    button_back = InlineKeyboardButton(text='Назад ↩️',
                                       callback_data=settings_daily_summary_callback.new(choice='back'))
    daily_summary_keyboard.row(button_back)

    return daily_summary_keyboard
