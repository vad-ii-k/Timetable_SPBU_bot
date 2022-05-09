import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.dispatcher.filters.builtin import CommandStart

from tgbot.loader import dp, db
from tgbot.keyboards.inline.choice_user_status_buttons import choice_user_status


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: Message, state: FSMContext) -> None:
    await state.finish()
    logging.info(f"start: id{message.from_user.id}")
    await message.answer(text=f"👋🏻 <b>Добро пожаловать, {message.from_user.full_name}!</b>\n"
                              f"Следуйте инструкциям для настройки.\n"
                              f"Получить расписание по:",
                         reply_markup=choice_user_status)
    await db.add_new_user()
