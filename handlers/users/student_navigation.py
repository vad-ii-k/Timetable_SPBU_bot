import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from handlers.users.helpers import send_group_schedule, change_message_to_progress
from keyboards.inline.callback_data import study_divisions_callback, study_levels_callback, study_programs_callback, \
    admission_years_callback, groups_callback
from keyboards.inline.student_navigaton_buttons import create_study_levels_keyboard, create_study_programs_keyboard, \
    create_admission_years_keyboard, create_groups_keyboard
from loader import dp
from utils.timetable.api import get_study_levels, get_groups


@dp.callback_query_handler(study_divisions_callback.filter())
async def study_divisions_keyboard_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")

    await change_message_to_progress(query.message)
    study_levels, response = await get_study_levels(callback_data["alias"])
    await query.message.edit_text("Выберите уровень подготовки:")
    await query.message.edit_reply_markup(reply_markup=await create_study_levels_keyboard(study_levels))
    await state.update_data(levels_response=response)


@dp.callback_query_handler(study_levels_callback.filter())
async def study_levels_keyboard_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")

    await query.message.edit_text("Выберите программу подготовки: ")
    data = await state.get_data()
    program_combinations = data["levels_response"][int(callback_data["serial"])]["StudyProgramCombinations"]
    await state.reset_data()
    await state.update_data(program_combinatons=program_combinations)

    programs = []
    for serial, program in enumerate(program_combinations):
        programs.append({"Name": program["Name"], "Serial": serial})
    await query.message.edit_reply_markup(reply_markup=await create_study_programs_keyboard(programs))


@dp.callback_query_handler(study_programs_callback.filter())
async def admission_years_keyboard_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")

    await query.message.edit_text("Выберите год поступления: ")
    data = await state.get_data()
    admission_years = data["program_combinatons"][int(callback_data["serial"])]["AdmissionYears"]
    await state.reset_data()

    years = []
    for year in admission_years:
        years.append({"Year": year["YearName"], "StudyProgramId": year["StudyProgramId"]})
    await query.message.edit_reply_markup(reply_markup=await create_admission_years_keyboard(years))


@dp.callback_query_handler(admission_years_callback.filter())
async def groups_keyboard_handler(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")

    await change_message_to_progress(query.message)
    groups = await get_groups(callback_data["program_id"])
    if len(groups) > 0:
        await query.message.edit_text("Выберите группу:")
        await query.message.edit_reply_markup(reply_markup=await create_groups_keyboard(groups))
    else:
        await query.message.edit_text("По данной программе группы не найдены!")
        await query.message.edit_reply_markup()


@dp.callback_query_handler(groups_callback.filter())
async def groups_keyboard_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")
    await send_group_schedule(query.message, callback_data, state, subscription=True)
