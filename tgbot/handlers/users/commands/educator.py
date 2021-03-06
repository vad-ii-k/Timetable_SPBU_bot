from aiogram.types import Message

from tgbot.loader import dp
from tgbot.states.choice_teacher import TeacherChoice


@dp.message_handler(commands="educator", state="*")
async def bot_educator_command(message: Message) -> None:
    """
    Handler for command: educator.

    :param message: message from user
    :return:
    """
    await message.answer("🔎 Введите фамилию преподавателя для поиска:")
    await TeacherChoice.getting_choice.set()
