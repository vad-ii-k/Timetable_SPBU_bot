import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters.builtin import CommandStart

from keyboards.inline.choice_user_status_buttons import choice_user_status
from loader import dp, db


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: Message, state: FSMContext):
    await state.finish()
    logging.info(f"start: id{message.from_user.id}")
    await message.answer(text=f"👋🏻 <b>Добро пожаловать, {message.from_user.full_name}!</b>\n"
                              f"Следуйте инструкциям для настройки бота.\n"
                              f"Получить расписание по:",
                         reply_markup=choice_user_status)
    await db.add_new_user()
