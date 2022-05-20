from aiogram.dispatcher.filters import CommandSettings
from aiogram.types import Message

from tgbot.keyboards.inline.settings_buttons import create_settings_keyboard
from tgbot.loader import dp, db


@dp.message_handler(CommandSettings(), state="*")
async def bot_settings_command(message: Message) -> None:
    """
    Handler for command: settings.

    :param message: message from user
    :return:
    """
    user_db = await db.get_user()
    settings = await db.set_settings()

    text = "📅 Основное расписание:\n — "
    student = await db.get_student(user_db)
    if student:
        group = await db.get_group(student.group_id)
        text += f"👨‍👩‍👧‍👦 {group.name}"
    else:
        teacher_user = await db.get_teacher_user(user_db)
        if teacher_user:
            teacher_spbu = await db.get_teacher_spbu(teacher_user.teacher_spbu_id)
            text += f"🧑‍🏫 {teacher_spbu.full_name}"
        else:
            text += "🚫 Отсутствует"

    text += "\n\n⚙️ Текущие настройки:"
    await message.answer(text=text, reply_markup=await create_settings_keyboard(settings))
