from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from tgbot.handlers.users.helpers import change_message_to_progress
from tgbot.keyboards.inline.callback_data import study_divisions_callback, \
    study_levels_callback, study_programs_callback, admission_years_callback
from tgbot.keyboards.inline.student_navigaton_buttons import create_study_levels_keyboard, \
    create_study_programs_keyboard, create_admission_years_keyboard, create_groups_keyboard
from tgbot.loader import dp
from utils.timetable.api import get_study_levels, get_groups


@dp.callback_query_handler(study_divisions_callback.filter())
async def study_divisions_keyboard_handler(
        query: CallbackQuery, callback_data: dict, state: FSMContext
) -> None:
    await change_message_to_progress(query.message)
    study_levels, response = await get_study_levels(callback_data["alias"])
    await query.message.edit_text("Выберите уровень подготовки:")
    await query.message.edit_reply_markup(
        reply_markup=await create_study_levels_keyboard(study_levels)
    )
    await state.update_data(levels_response=response)


@dp.callback_query_handler(study_levels_callback.filter())
async def study_levels_keyboard_handler(
        query: CallbackQuery, callback_data: dict, state: FSMContext
) -> None:
    await query.message.edit_text("Выберите программу подготовки: ")
    data = await state.get_data()
    serial: int = int(callback_data["serial"])
    program_combinations = data["levels_response"][serial]["StudyProgramCombinations"]
    await state.reset_data()
    await state.update_data(program_combinatons=program_combinations)

    programs = []
    for serial, program in enumerate(program_combinations):
        programs.append({"Name": program["Name"], "Serial": serial})
    await query.message.edit_reply_markup(
        reply_markup=await create_study_programs_keyboard(programs)
    )


@dp.callback_query_handler(study_programs_callback.filter())
async def admission_years_keyboard_handler(
        query: CallbackQuery, callback_data: dict, state: FSMContext
) -> None:
    await query.message.edit_text("Выберите год поступления: ")
    data = await state.get_data()
    serial: int = int(callback_data["serial"])
    admission_years = data["program_combinatons"][serial]["AdmissionYears"]
    await state.reset_data()

    years = []
    for year in admission_years:
        years.append({"Year": year["YearName"], "StudyProgramId": year["StudyProgramId"]})
    await query.message.edit_reply_markup(reply_markup=await create_admission_years_keyboard(years))


@dp.callback_query_handler(admission_years_callback.filter())
async def groups_keyboard_handler(query: CallbackQuery, callback_data: dict) -> None:
    await change_message_to_progress(query.message)
    groups = await get_groups(callback_data["program_id"])
    if len(groups) > 0:
        await query.message.edit_text("Выберите группу:")
        await query.message.edit_reply_markup(reply_markup=await create_groups_keyboard(groups))
    else:
        await query.message.edit_text("По данной программе группы не найдены!")
        await query.message.edit_reply_markup()
