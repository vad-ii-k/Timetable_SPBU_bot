from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InputFile

from tgbot.keyboards.inline.schedule_subscription_buttons import create_schedule_subscription_keyboard
from tgbot.keyboards.inline.timetable_buttons import create_timetable_keyboard
from tgbot.loader import db
from utils.timetable.get_timetable import get_timetable


async def change_message_to_progress(message: Message, is_picture: bool = False) -> None:
    if is_picture:
        await message.edit_caption("🕒 <i>Загрузка...</i>")
    else:
        await message.edit_text("⏳")


async def send_schedule(message: Message, callback_data: dict, state: FSMContext, subscription: bool) -> None:
    await change_message_to_progress(message, await check_message_content_type(message))

    settings = await db.set_settings()
    is_picture: bool = settings.schedule_view_is_picture
    text = await get_timetable(tt_id=int(callback_data["tt_id"]), user_type=callback_data["user_type"],
                               is_picture=is_picture, week_counter=0)
    answer_msg = await create_answer_based_on_content(message, text, is_picture)

    await state.update_data(user_type=callback_data["user_type"], tt_id=callback_data["tt_id"])
    await answer_msg.edit_reply_markup(reply_markup=await create_timetable_keyboard(is_picture=is_picture))

    if subscription:
        await send_subscription_question(answer_msg)


async def create_answer_based_on_content(message: Message, text: str, is_picture: bool) -> Message:
    if is_picture:
        answer_msg = await message.answer_photo(photo=InputFile("utils/image_converter/output.png"))
        await answer_msg.edit_caption(caption=text)
        await message.delete()
    else:
        answer_msg = await message.edit_text(text)
    return answer_msg


async def send_subscription_question(message: Message) -> None:
    answer_sub = await message.answer(text="⚙️ Хотите сделать это расписание своим основным?")
    await answer_sub.edit_reply_markup(reply_markup=await create_schedule_subscription_keyboard())


async def check_message_content_type(message: Message) -> bool:
    is_picture = (message.content_type == 'photo')
    return is_picture
