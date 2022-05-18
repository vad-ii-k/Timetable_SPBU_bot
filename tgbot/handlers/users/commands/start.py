import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import Message

from tgbot.keyboards.inline.choice_user_status_buttons import choice_user_status
from tgbot.loader import dp, db


@dp.message_handler(CommandStart(), state="*")
async def bot_start_command(message: Message, state: FSMContext) -> None:
    """
    Handler for command: start.

    :param message: message from user
    :param state: user's state
    :return:
    """
    await state.finish()
    logging.info("start: id%s", message.from_user.id)
    await message.answer(
        text=f"👋🏻 <b>Добро пожаловать, {message.from_user.full_name}!</b>\n"
             "ℹ️ Следуйте указаниям для настройки\n"
             "❕ Для корректной работы взаимодействуйте только с последним сообщением бота\n"
             "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
             "⬇️ Получить расписание по:",
        reply_markup=choice_user_status,
    )
    await db.add_new_user()
