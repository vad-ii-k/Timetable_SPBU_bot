from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.handlers.users.helpers import send_schedule
from tgbot.loader import dp, db


@dp.message_handler(commands="my_schedule", state="*")
async def bot_my_schedule_command(query: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for command: my_schedule.

    :param query: callback query
    :param state: user's state
    :return:
    """
    user_db = await db.get_user()
    student = await db.get_student(user_db)
    message: Message = await query.answer("...")
    if student:
        group = await db.get_group(student.group_id)
        await send_schedule(message, {"tt_id": group.tt_id, "user_type": 'student'}, state, False)
    else:
        teacher_user = await db.get_teacher_user(user_db)
        if teacher_user:
            teacher_spbu = await db.get_teacher_spbu(teacher_user.teacher_spbu_id)
            await send_schedule(message, {"tt_id": teacher_spbu.tt_id, "user_type": 'teacher'},
                                state, False)
        else:
            text = "🚫 Основное расписание отсутствует\n" \
                   "1. 🔎 Воспользуйтесь одной из команд:\n" \
                   "      /start, /group или /educator\n" \
                   "2. 🔖 Выберите нужное Вам расписание\n" \
                   "3. ✅ Сделайте расписание основным"
            await message.answer(text)
            await message.delete()
