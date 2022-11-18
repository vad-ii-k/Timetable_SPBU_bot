""" Handling the keyboard with a schedule """
import asyncio

from aiogram import Router, F, flags
from aiogram.filters import and_f
from aiogram.types import CallbackQuery

from tgbot.misc.cb_data import ScheduleCallbackFactory
from tgbot.handlers.helpers import change_message_to_loading, schedule_keyboard_helper, delete_message
from tgbot.services.schedule.getting_shedule import (
    get_text_week_schedule,
    get_text_day_schedule,
    get_image_week_schedule,
    get_image_day_schedule,
)

router = Router()


@router.callback_query(ScheduleCallbackFactory.filter(F.button.in_({"1-1", "1-2", "1-3"})))
@flags.chat_action('typing')
async def schedule_days_callback(callback: CallbackQuery, callback_data: ScheduleCallbackFactory):
    """
    Handling button clicks to change the day using a scheduled keyboard
    :param callback:
    :param callback_data:
    """
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
    tt_id, user_type, day_counter = callback_data.tt_id, callback_data.user_type, callback_data.day_counter
    if callback.message.content_type == "document":
        text, photo = await get_image_day_schedule(tt_id, user_type, day_counter=day_counter)
        await schedule_keyboard_helper(callback, callback_data, text, photo)
    else:
        text = await get_text_day_schedule(tt_id, user_type, day_counter=day_counter)
        await schedule_keyboard_helper(callback, callback_data, text)
    await callback.answer(cache_time=2)
    asyncio.create_task(delete_message(callback.message, 0))


@router.callback_query(ScheduleCallbackFactory.filter(F.button.in_({"2-1", "2-2"})))
@flags.chat_action('typing')
async def schedule_weeks_callback(callback: CallbackQuery, callback_data: ScheduleCallbackFactory):
    """
    Handling button clicks to change the week using a scheduled keyboard
    :param callback:
    :param callback_data:
    """
    await change_message_to_loading(callback.message)
    callback_data.day_counter = None
    if callback_data.week_counter is None:
        callback_data.week_counter = 0
    match callback_data.button:
        case "2-1":
            callback_data.week_counter = 0
        case "2-2":
            callback_data.week_counter += 1
    tt_id, user_type, week_counter = callback_data.tt_id, callback_data.user_type, callback_data.week_counter
    if callback.message.content_type == "document":
        text, photo = await get_image_week_schedule(tt_id, user_type, week_counter=week_counter)
        await schedule_keyboard_helper(callback, callback_data, text, photo)
    else:
        text, _ = await get_text_week_schedule(tt_id, user_type, week_counter=week_counter)
        await schedule_keyboard_helper(callback, callback_data, text)
    await callback.answer(cache_time=2)
    asyncio.create_task(delete_message(callback.message, 0))


@router.callback_query(and_f(ScheduleCallbackFactory.filter(F.button == "3-1"), F.message.document))
@flags.chat_action('typing')
async def schedule_document_callback(callback: CallbackQuery, callback_data: ScheduleCallbackFactory):
    """
    Handling button clicks to change the schedule view using a scheduled keyboard
    :param callback:
    :param callback_data:
    """
    await change_message_to_loading(callback.message)
    tt_id, user_type = callback_data.tt_id, callback_data.user_type
    if callback_data.week_counter is not None:
        text, _ = await get_text_week_schedule(tt_id, user_type, week_counter=callback_data.week_counter)
        await schedule_keyboard_helper(callback, callback_data, text)
    else:
        text = await get_text_day_schedule(tt_id, user_type, day_counter=callback_data.day_counter)
        await schedule_keyboard_helper(callback, callback_data, text)
    await callback.answer(cache_time=2)
    asyncio.create_task(delete_message(callback.message, 0))


@router.callback_query(and_f(ScheduleCallbackFactory.filter(F.button == "3-1"), ~F.message.document))
@flags.chat_action('upload_document')
async def schedule_text_callback(callback: CallbackQuery, callback_data: ScheduleCallbackFactory):
    """
    Handling button clicks to change the schedule view using a scheduled keyboard
    :param callback:
    :param callback_data:
    """
    await change_message_to_loading(callback.message)
    tt_id, user_type = callback_data.tt_id, callback_data.user_type
    if callback_data.week_counter is not None:
        text, photo = await get_image_week_schedule(tt_id, user_type, week_counter=callback_data.week_counter)
        await schedule_keyboard_helper(callback, callback_data, text, photo)
    else:
        text, photo = await get_image_day_schedule(tt_id, user_type, day_counter=callback_data.day_counter)
        await schedule_keyboard_helper(callback, callback_data, text, photo)
    await callback.answer(cache_time=2)
    asyncio.create_task(delete_message(callback.message, 0))
