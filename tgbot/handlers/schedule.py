from aiogram import Router
from aiogram.types import CallbackQuery
from magic_filter import F

from tgbot.cb_data import ScheduleCallbackFactory
from tgbot.handlers.helpers import change_message_to_loading, schedule_keyboard_helper
from tgbot.services.schedule.getting_shedule import get_schedule

router = Router()


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
    tt_id, user_type, week_counter = callback_data.tt_id, callback_data.user_type, callback_data.week_counter
    text, _ = await get_schedule(tt_id=tt_id, user_type=user_type, week_counter=week_counter)
    await schedule_keyboard_helper(callback, text, tt_id, user_type, callback_data.day_counter)
    await callback.answer(cache_time=2)
    await callback.message.delete()
