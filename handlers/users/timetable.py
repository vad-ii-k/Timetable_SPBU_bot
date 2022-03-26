import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from datetime import date, timedelta

from keyboards.inline.callback_data import timetable_callback
from keyboards.inline.timetable_buttons import create_timetable_keyboard
from loader import dp
from utils.tt_api import teacher_timetable_week


@dp.callback_query_handler(timetable_callback.filter())
async def timetable_keyboard_handler(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=1)
    logging.info(f"call = {callback_data}")
    data = await state.get_data()

    await call.message.edit_text(text="Other",
                                 reply_markup=await create_timetable_keyboard())
