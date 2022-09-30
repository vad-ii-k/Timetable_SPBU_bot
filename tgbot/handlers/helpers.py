from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from tgbot.cb_data import TTObjectChoiceCallbackFactory
from tgbot.keyboards.inline import create_schedule_keyboard
from tgbot.services.schedule.getting_shedule import get_schedule


async def change_message_to_loading(message: Message) -> bool:
    message_content_type_is_photo = message.content_type == "photo"
    if message_content_type_is_photo:
        await message.edit_caption(_("🕒 <i>Загрузка...</i>"))
    else:
        await message.edit_text("⏳")
    return message_content_type_is_photo


async def send_schedule(message: Message, callback_data: TTObjectChoiceCallbackFactory, subscription: bool) -> None:
    await change_message_to_loading(message)
    # settings = await db.set_settings()
    # is_picture: bool = settings.schedule_view_is_picture
    is_photo = False
    text = await get_schedule(tt_id=int(callback_data.tt_id), user_type=callback_data.user_type)
# await get_timetable(tt_id=callback_data.tt_id, user_type=callback_data.user_type, is_photo=is_photo, week_counter=0)
    await message.delete()
    answer_msg = await message.answer(text=text)
    await answer_msg.edit_reply_markup(reply_markup=await create_schedule_keyboard(
        is_photo=is_photo, tt_id=int(callback_data.tt_id), user_type=callback_data.user_type)
    )
    # if subscription:
    #     await send_subscription_question(answer_msg)
