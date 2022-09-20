from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tgbot.cb_data import (
    StudyDivisionCallbackFactory,
    StudyLevelCallbackFactory,
    ProgramCombinationsCallbackFactory,
    AdmissionYearsCallbackFactory,
)
from tgbot.data_classes import StudyLevel, ProgramCombination
from tgbot.handlers.helpers import change_message_to_loading
from tgbot.keyboards.inline import (
    create_study_levels_keyboard,
    create_study_programs_keyboard,
    create_admission_years_keyboard,
    create_groups_keyboard,
)
from tgbot.misc.states import SearchGroup
from tgbot.services.timetable_api.timetable_api import get_study_levels, get_groups

router = Router()


@router.callback_query(StudyDivisionCallbackFactory.filter(), flags={'chat_action': 'typing'})
async def study_divisions_navigation_callback(
        callback: CallbackQuery, callback_data: StudyDivisionCallbackFactory, state: FSMContext
):
    await change_message_to_loading(callback.message)
    study_levels = await get_study_levels(callback_data.alias)
    await callback.message.delete()
    await callback.message.answer(
        text="⬇️ Выберите уровень подготовки:",
        reply_markup=await create_study_levels_keyboard(study_levels)
    )
    await state.update_data(study_levels=study_levels)


@router.callback_query(StudyLevelCallbackFactory.filter())
async def study_levels_navigation_callback(
        callback: CallbackQuery, callback_data: StudyLevelCallbackFactory, state: FSMContext
):
    data = await state.get_data()
    study_level: StudyLevel = data["study_levels"][int(callback_data.serial)]
    await state.set_data({})
    await state.update_data(program_combinatons=study_level.program_combinations)

    await callback.message.edit_text(
        text="⬇️ Выберите программу подготовки: ",
        reply_markup=await create_study_programs_keyboard(study_level.program_combinations)
    )


@router.callback_query(ProgramCombinationsCallbackFactory.filter())
async def admission_years_navigation_callback(
        callback: CallbackQuery, callback_data: ProgramCombinationsCallbackFactory, state: FSMContext
):
    data = await state.get_data()
    program_combinaton: ProgramCombination = data["program_combinatons"][int(callback_data.serial)]
    await state.set_data({})

    await callback.message.edit_text(
        text="⬇️ Выберите год поступления: ",
        reply_markup=await create_admission_years_keyboard(program_combinaton.admission_years)
    )


@router.callback_query(AdmissionYearsCallbackFactory.filter(), flags={'chat_action': 'typing'})
async def group_choice_navigation_callback(
        callback: CallbackQuery, callback_data: AdmissionYearsCallbackFactory, state: FSMContext):
    await change_message_to_loading(callback.message)
    groups = await get_groups(callback_data.study_program_id)
    await callback.message.delete()
    if len(groups) > 0:
        await callback.message.answer(
            text="⬇️ Выберите группу:",
            reply_markup=await create_groups_keyboard(groups)
        )
        await state.set_state(SearchGroup.choosing)
    else:
        await callback.message.edit_text("❌ По данной программе группы не найдены!")
