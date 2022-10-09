from aiogram import Router
from aiogram.types import CallbackQuery
from magic_filter import F

from tgbot.cb_data import ScheduleCallbackFactory
from tgbot.handlers.helpers import change_message_to_loading, schedule_keyboard_helper
from tgbot.keyboards.inline import create_schedule_keyboard
from tgbot.services.schedule.getting_shedule import get_text_week_schedule, get_text_day_schedule, get_image_schedule

router = Router()


@router.callback_query(
    ScheduleCallbackFactory.filter(F.button.in_({"1-1", "1-2", "1-3"})), flags={'chat_action': 'typing'}
)
async def schedule_days_callback(callback: CallbackQuery, callback_data: ScheduleCallbackFactory):
    await change_message_to_loading(callback.message)
    callback_data.week_counter = None
    if callback_data.day_counter is None:
        callback_data.day_counter = 0
    match callback_data.button:
        case "1-1":
            callback_data.day_counter -= 1
        case "1-2":
            callback_data.day_counter = 0
        case "1-3":
            callback_data.day_counter += 1

    text = await get_text_day_schedule(
        callback_data.tt_id, callback_data.user_type, day_counter=callback_data.day_counter
    )
    await schedule_keyboard_helper(callback, callback_data, text)
    await callback.answer(cache_time=2)
    await callback.message.delete()


@router.callback_query(ScheduleCallbackFactory.filter(F.button.in_({"2-1", "2-2"})), flags={'chat_action': 'typing'})
async def schedule_weeks_callback(callback: CallbackQuery, callback_data: ScheduleCallbackFactory):
    await change_message_to_loading(callback.message)
    callback_data.day_counter = None
    if callback_data.week_counter is None:
        callback_data.week_counter = 0
    match callback_data.button:
        case "2-1":
            callback_data.week_counter = 0
        case "2-2":
            callback_data.week_counter += 1
    is_photo = callback.message.content_type == "photo"
    if is_photo:
        text, photo = await get_image_schedule()
        await schedule_keyboard_helper(callback, callback_data, text, photo)
    else:
        text, _ = await get_text_week_schedule(
            callback_data.tt_id, callback_data.user_type, week_counter=callback_data.week_counter
        )
        await schedule_keyboard_helper(callback, callback_data, text)
    await callback.answer(cache_time=2)
    await callback.message.delete()


@router.callback_query(ScheduleCallbackFactory.filter(F.button == "3-1"), flags={'chat_action': 'typing'})
async def schedule_photo_callback(callback: CallbackQuery, callback_data: ScheduleCallbackFactory):
    await change_message_to_loading(callback.message)
    text, photo = await get_image_schedule()
    reply_markup = await create_schedule_keyboard(is_photo=True, callback_data=callback_data)
    await callback.message.answer_photo(photo=photo, caption=text, reply_markup=reply_markup)
    await callback.answer(cache_time=2)
    await callback.message.delete()
