from aiogram.contrib.middlewares import logging
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters.builtin import CommandStart

from keyboards.inline.choice_user_status_buttons import choice_user_status
from loader import dp


@dp.message_handler(CommandStart())
async def bot_start(message: Message):
    await message.answer(text=f"Добро пожаловать, {message.from_user.full_name}!\n"
                              f"Следуйте инструкциям для настройки бота.\n"
                              f"Выберите соответствующую кнопку:",
                         reply_markup=choice_user_status)
