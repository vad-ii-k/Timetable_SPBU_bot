import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.inline.callback_data import timetable_callback
from keyboards.inline.timetable_buttons import create_timetable_keyboard
from loader import dp
from utils.tt_api import teacher_timetable_week


@dp.callback_query_handler(timetable_callback.filter(button='2-1'))
async def timetable_keyboard_handler_2_1(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=2)
    logging.info(f"call = {callback_data}")
    await state.update_data(week_counter=0)
    data = await state.get_data()
    if data.get("week_counter") is not None:
        await call.message.edit_text("Получение расписания...")
        await call.message.edit_text(text=await teacher_timetable_week(teacher_id=callback_data["Id"],
                                                                       week_counter=data.get("week_counter")),
                                     reply_markup=await create_timetable_keyboard(user_type=callback_data["type"],
                                                                                  tt_id=callback_data["Id"]))


@dp.callback_query_handler(timetable_callback.filter(button='2-2'))
async def timetable_keyboard_handler_2_2(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=3)
    logging.info(f"call = {callback_data}")
    data = await state.get_data()
    if data.get("week_counter") is not None:
        await state.update_data(week_counter=data.get("week_counter") + 1)
    else:
        await state.update_data(week_counter=1)
    data = await state.get_data()
    await call.message.edit_text("Получение расписания...")
    await call.message.edit_text(text=await teacher_timetable_week(teacher_id=callback_data["Id"],
                                                                   week_counter=data.get("week_counter")),
                                 reply_markup=await create_timetable_keyboard(user_type=callback_data["type"],
                                                                              tt_id=callback_data["Id"]))
