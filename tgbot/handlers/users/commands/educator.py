from aiogram.types import Message

from tgbot.loader import dp
from tgbot.states.choice_teacher import TeacherChoice


@dp.message_handler(commands='educator', state="*")
async def bot_educator_command(message: Message) -> None:
    await message.answer("🔎 Введите фамилию преподавателя для поиска:")
    await TeacherChoice.getting_choice.set()
