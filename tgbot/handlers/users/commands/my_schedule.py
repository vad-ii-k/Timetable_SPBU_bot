from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.handlers.users.helpers import send_teacher_schedule, send_group_schedule
from tgbot.loader import dp, db


@dp.message_handler(commands='my_schedule', state="*")
async def bot_my_schedule_command(query: CallbackQuery, state: FSMContext):
    user_db = await db.get_user()
    student = await db.get_student(user_db)
    message: Message = await query.answer('...')
    if student:
        group = await db.get_group(student.group_id)
        await send_group_schedule(message, {"group_id": group.tt_id, "group_name": group.name}, state, False)
    else:
        teacher_user = await db.get_teacher_user(user_db)
        if teacher_user:
            teacher_spbu = await db.get_teacher_spbu(teacher_user.teacher_spbu_id)
            await send_teacher_schedule(message, {"teacher_id": teacher_spbu.tt_id}, state, False)
        else:
            text = "🚫 Основное расписание отсутствует"
            await message.answer(text)
            await message.delete()
