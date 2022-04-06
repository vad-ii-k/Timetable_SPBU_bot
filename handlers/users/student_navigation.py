import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputFile

from keyboards.inline.callback_data import study_divisions_callback, study_levels_callback, study_programs_callback, \
    admission_years_callback, groups_callback
from keyboards.inline.schedule_subscription_buttons import create_schedule_subscription_keyboard
from keyboards.inline.student_navigaton_buttons import create_study_levels_keyboard, create_study_programs_keyboard, \
    create_admission_years_keyboard, create_groups_keyboard
from keyboards.inline.timetable_buttons import create_timetable_keyboard
from loader import dp, db
from utils.tt_api import get_study_levels, get_groups, group_timetable_week


@dp.callback_query_handler(study_divisions_callback.filter())
async def study_divisions_keyboard_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")

    await query.message.edit_text("<i>Подождите...</i>")
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
    program_combinatons = data["levels_response"][int(callback_data["serial"])]["StudyProgramCombinations"]
    await state.reset_data()
    await state.update_data(program_combinatons=program_combinatons)

    programs = []
    for serial, program in enumerate(program_combinatons):
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

    await query.message.edit_text("<i>Подождите...</i>")
    groups = await get_groups(callback_data["program_id"])
    await query.message.edit_text("Выберите группу:")
    await query.message.edit_reply_markup(reply_markup=await create_groups_keyboard(groups))


@dp.callback_query_handler(groups_callback.filter())
async def groups_keyboard_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")

    settings = await db.get_settings(query.from_user.id)
    is_picture = settings.schedule_view_is_picture
    await query.message.edit_text("<i>Получение расписания...</i>")
    text = await group_timetable_week(callback_data["group_id"])
    if is_picture:
        answer = await query.message.answer_photo(photo=InputFile("utils/image_converter/output.png"))
        await query.message.delete()
    else:
        answer = await query.message.edit_text(text)
    await state.update_data(user_type="student", tt_id=callback_data["group_id"])
    await answer.edit_reply_markup(reply_markup=await create_timetable_keyboard(is_picture=is_picture))

    await answer.answer(text="Хотите сделать это расписание своим основным?",
                        reply_markup=await create_schedule_subscription_keyboard())
