import pickle

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from tgbot.cb_data import (
    StudyDivisionCallbackFactory,
    StudyLevelCallbackFactory,
    ProgramCombinationsCallbackFactory,
    AdmissionYearsCallbackFactory,
)
from tgbot.data_classes import ProgramCombination, StudyLevel
from tgbot.handlers.helpers import change_message_to_loading
from tgbot.keyboards.inline import (
    create_study_levels_keyboard,
    create_study_programs_keyboard,
    create_admission_years_keyboard,
    create_groups_keyboard,
)
from tgbot.misc.states import Searching
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
        text=_("⬇️ Выберите уровень подготовки:"),
        reply_markup=await create_study_levels_keyboard(study_levels)
    )
    await state.set_data({"study_levels": pickle.dumps(study_levels)})


@router.callback_query(StudyLevelCallbackFactory.filter())
async def study_levels_navigation_callback(
        callback: CallbackQuery, callback_data: StudyLevelCallbackFactory, state: FSMContext
):
    data = await state.get_data()
    study_levels: list[StudyLevel] = pickle.loads(data["study_levels"])
    program_combinations = study_levels[callback_data.serial].program_combinations
    await state.set_data({"program_combinations": pickle.dumps(program_combinations)})

    await callback.message.edit_text(
        text=_("⬇️ Выберите программу подготовки: "),
        reply_markup=await create_study_programs_keyboard(program_combinations)
    )


@router.callback_query(ProgramCombinationsCallbackFactory.filter())
async def admission_years_navigation_callback(
        callback: CallbackQuery, callback_data: ProgramCombinationsCallbackFactory, state: FSMContext
):
    data = await state.get_data()
    program_combinations: list[ProgramCombination] = pickle.loads(data["program_combinations"])
    admission_years = program_combinations[callback_data.serial].admission_years
    await state.set_data({})

    await callback.message.edit_text(
        text=_("⬇️ Выберите год поступления: "),
        reply_markup=await create_admission_years_keyboard(admission_years)
    )


@router.callback_query(AdmissionYearsCallbackFactory.filter(), flags={'chat_action': 'typing'})
async def group_choice_navigation_callback(
        callback: CallbackQuery, callback_data: AdmissionYearsCallbackFactory, state: FSMContext
):
    await change_message_to_loading(callback.message)
    groups = await get_groups(callback_data.study_program_id)
    if len(groups) > 0:
        await callback.message.answer(
            text=_("⬇️ Выберите группу:"),
            reply_markup=await create_groups_keyboard(groups)
        )
        await state.set_state(Searching.choosing)
    else:
        await callback.message.edit_text(_("❌ По данной программе группы не найдены!"))
    await callback.message.delete()
