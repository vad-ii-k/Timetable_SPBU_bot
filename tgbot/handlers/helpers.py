from aiogram.types import Message, BufferedInputFile, URLInputFile

from tgbot.cb_data import TTObjectChoiceCallbackFactory
from tgbot.keyboards.inline import create_schedule_keyboard


async def change_message_to_loading(message: Message) -> bool:
    message_content_type_is_photo = message.content_type == "photo"
    if message_content_type_is_photo:
        await message.edit_caption("🕒 <i>Загрузка...</i>")
    else:
        await message.edit_text("⏳")
    return message_content_type_is_photo


async def create_message_based_on_content(
        message: Message, text: str, is_photo: bool, photo: BufferedInputFile | None = None
) -> Message:
    if is_photo:
        answer_msg = await message.answer_photo(photo=photo, caption=text)
        await message.delete()
    else:
        answer_msg = await message.edit_text(text)
    return answer_msg


async def send_schedule(message: Message, callback_data: TTObjectChoiceCallbackFactory, subscription: bool) -> None:
    await change_message_to_loading(message)
    # settings = await db.set_settings()
    # is_picture: bool = settings.schedule_view_is_picture
    is_photo = True
    text = "text"
# await get_timetable(tt_id=callback_data.tt_id, user_type=callback_data.user_type, is_photo=is_photo, week_counter=0)
    answer_msg = await create_message_based_on_content(message, text, is_photo)
    await answer_msg.edit_reply_markup(reply_markup=await create_schedule_keyboard(
        is_photo=is_photo, tt_id=int(callback_data.tt_id), user_type=callback_data.user_type)
    )
    # if subscription:
    #     await send_subscription_question(answer_msg)
