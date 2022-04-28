from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from handlers.users.helpers import send_teacher_schedule, send_group_schedule
from loader import dp, db


@dp.message_handler(commands='my_schedule', state="*")
async def bot_my_schedule_command(query: CallbackQuery, state: FSMContext):
    user_db = await db.get_user()
    student = await db.get_student(user_db)
    message: Message = await query.answer('...')
    if student:
        group = await db.get_group(student.group_id)
        await send_group_schedule(message, {"group_id": group.tt_id, "group_name": group.name}, state, False)
    else:
        teacher = await db.get_teacher(user_db)
        if teacher:
            await send_teacher_schedule(message, {"teacher_id": teacher.tt_id}, state, subscription=False)
        else:
            text = "🚫 Основное расписание отсутствует"
            await message.answer(text)
