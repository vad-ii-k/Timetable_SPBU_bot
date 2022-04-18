from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile

from keyboards.inline.schedule_subscription_buttons import create_schedule_subscription_keyboard
from keyboards.inline.timetable_buttons import create_timetable_keyboard
from loader import db
from utils.timetable.api import get_teacher_timetable_week
from utils.timetable.get_timetable import get_group_timetable


async def change_message_to_progress(message: Message):
    await message.edit_text("🕒 <i>Получение расписания...</i>")


async def send_group_schedule(query: CallbackQuery, callback_data: dict, state: FSMContext):
    settings = await db.set_settings()
    is_picture = settings.schedule_view_is_picture
    await change_message_to_progress(query.message)

    text = await get_group_timetable(tt_id=int(callback_data["group_id"]), week_counter=0)
    answer_msg = await create_answer_based_on_content(query, text, is_picture)

    await state.update_data(user_type="student", tt_id=callback_data["group_id"],
                            group_name=text.split('\n', 1)[0])
    await answer_msg.edit_reply_markup(reply_markup=await create_timetable_keyboard(is_picture=is_picture))

    await send_subscription_question(answer_msg)


async def send_teacher_schedule(query: CallbackQuery, callback_data: dict, state: FSMContext):
    settings = await db.set_settings()
    is_picture = settings.schedule_view_is_picture
    await change_message_to_progress(query.message)

    text = await get_teacher_timetable_week(callback_data.get("teacher_id"))
    answer_msg = await create_answer_based_on_content(query, text, is_picture)

    await state.update_data(user_type="teacher", tt_id=callback_data.get("teacher_id"),
                            full_name=text.split('\n', 1)[0].split(' ', 1)[1])
    await answer_msg.edit_reply_markup(reply_markup=await create_timetable_keyboard(is_picture=is_picture))

    await send_subscription_question(answer_msg)


async def create_answer_based_on_content(query: CallbackQuery, text: str, is_picture: bool) -> Message:
    if is_picture:
        answer_msg = await query.message.answer_photo(photo=InputFile("utils/image_converter/output.png"))
        await answer_msg.edit_caption(caption=text.split('\n')[1] + "\nТЕСТОВЫЙ РЕЖИМ!!!")
        await query.message.delete()
    else:
        answer_msg = await query.message.edit_text(text)
    return answer_msg


async def send_subscription_question(answer_msg: Message):
    answer_sub = await answer_msg.answer(text="⚙️ Хотите сделать это расписание своим основным?")
    await answer_sub.edit_reply_markup(reply_markup=await create_schedule_subscription_keyboard())


async def check_message_content_type(query: CallbackQuery) -> bool:
    is_picture = (query.message.content_type == 'photo')
    if is_picture:
        await query.message.edit_caption("🕒 <i>Получение расписания...</i>")
    else:
        await change_message_to_progress(query.message)
    return is_picture
