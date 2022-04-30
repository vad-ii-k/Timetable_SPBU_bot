from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile

from tgbot.keyboards.inline.schedule_subscription_buttons import create_schedule_subscription_keyboard
from tgbot.keyboards.inline.timetable_buttons import create_timetable_keyboard
from tgbot.loader import db
from utils.timetable.api import get_teacher_timetable_week
from utils.timetable.get_timetable import get_group_timetable


async def change_message_to_progress(message: Message, is_picture: bool = False):
    if is_picture:
        await message.edit_caption("🕒 <i>Загрузка...</i>")
    else:
        await message.edit_text("🕒 <i>Загрузка...</i>")


async def send_group_schedule(message: Message, callback_data: dict, state: FSMContext, subscription: bool):
    settings = await db.set_settings()
    is_picture: bool = settings.schedule_view_is_picture
    await change_message_to_progress(message, is_picture)

    text = await get_group_timetable(tt_id=int(callback_data["group_id"]), is_picture=is_picture, week_counter=0)
    answer_msg = await create_answer_based_on_content(message, text, is_picture)

    await state.update_data(user_type="student", tt_id=callback_data["group_id"],
                            group_name=text.split('\n', 1)[0])
    await answer_msg.edit_reply_markup(reply_markup=await create_timetable_keyboard(is_picture=is_picture))

    if subscription:
        await send_subscription_question(answer_msg)


async def send_teacher_schedule(message: Message, callback_data: dict, state: FSMContext, subscription: bool):
    settings = await db.set_settings()
    is_picture = settings.schedule_view_is_picture
    await change_message_to_progress(message, is_picture)

    text = await get_teacher_timetable_week(callback_data.get("teacher_id"))
    answer_msg = await create_answer_based_on_content(message, text, is_picture)

    await state.update_data(user_type="teacher", tt_id=callback_data.get("teacher_id"),
                            full_name=text.split('\n', 1)[0].split(' ', 1)[1])
    await answer_msg.edit_reply_markup(reply_markup=await create_timetable_keyboard(is_picture=is_picture))

    if subscription:
        await send_subscription_question(answer_msg)


async def create_answer_based_on_content(message: Message, text: str, is_picture: bool) -> Message:
    if is_picture:
        answer_msg = await message.answer_photo(photo=InputFile("utils/image_converter/output.png"))
        await answer_msg.edit_caption(caption=text.split('\n')[1] + "\nТЕСТОВЫЙ РЕЖИМ!!!")
        await message.delete()
    else:
        answer_msg = await message.edit_text(text)
    return answer_msg


async def send_subscription_question(answer_msg: Message):
    answer_sub = await answer_msg.answer(text="⚙️ Хотите сделать это расписание своим основным?")
    await answer_sub.edit_reply_markup(reply_markup=await create_schedule_subscription_keyboard())


async def check_message_content_type(query: CallbackQuery) -> bool:
    is_picture = (query.message.content_type == 'photo')
    return is_picture
