import asyncio
from contextlib import suppress

from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from tgbot.cb_data import TTObjectChoiceCallbackFactory
from tgbot.keyboards.inline import create_schedule_keyboard, create_schedule_subscription_keyboard
from tgbot.services.db_api.db_commands import database
from tgbot.services.schedule.getting_shedule import get_schedule


async def change_message_to_loading(message: Message) -> bool:
    message_content_type_is_photo = message.content_type == "photo"
    if message_content_type_is_photo:
        await message.edit_caption(_("🕒 <i>Загрузка...</i>"))
    else:
        await message.edit_text("⏳")
    return message_content_type_is_photo


async def delete_message(message: Message, sleep_time: int = 0) -> None:
    await asyncio.sleep(sleep_time)
    with suppress(TelegramAPIError):
        await message.delete()


async def send_subscription_question(message: Message) -> None:
    answer_sub = await message.answer(text=_("⚙️ Хотите сделать это расписание своим основным?"))
    await answer_sub.edit_reply_markup(reply_markup=await create_schedule_subscription_keyboard())
    asyncio.create_task(delete_message(answer_sub, 30))


async def send_schedule(
        callback: CallbackQuery, callback_data: TTObjectChoiceCallbackFactory, subscription: bool
) -> None:
    await change_message_to_loading(callback.message)
    user = await database.get_user(tg_user_id=callback.from_user.id)
    settings = await database.get_settings(user)
    is_picture: bool = settings.schedule_view_is_picture

    text = await get_schedule(tt_id=int(callback_data.tt_id), user_type=callback_data.user_type)
# await get_timetable(tt_id=callback_data.tt_id, user_type=callback_data.user_type, is_photo=is_photo, week_counter=0)
    await callback.message.delete()
    answer_msg = await callback.message.answer(text=text)
    await answer_msg.edit_reply_markup(reply_markup=await create_schedule_keyboard(
        is_photo=is_picture, tt_id=int(callback_data.tt_id), user_type=callback_data.user_type)
    )
    if subscription:
        await send_subscription_question(answer_msg)
