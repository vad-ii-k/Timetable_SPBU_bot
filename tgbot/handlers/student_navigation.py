""" Handling program navigation to select a student's group """
from aiogram import Router, flags
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from tgbot.handlers.helpers import change_message_to_loading
from tgbot.keyboards.inline import (
    create_admission_years_keyboard,
    create_groups_keyboard,
    create_study_levels_keyboard,
    create_study_programs_keyboard,
)
from tgbot.misc.cb_data import (
    AdmissionYearsCallbackFactory,
    ProgramCombinationsCallbackFactory,
    StudyDivisionCallbackFactory,
    StudyLevelCallbackFactory,
)
from tgbot.misc.states import Searching
from tgbot.services.timetable_api.timetable_api import get_groups, get_study_levels

router = Router()


@router.callback_query(StudyDivisionCallbackFactory.filter())
@flags.chat_action(ChatAction.TYPING)
async def study_divisions_navigation_callback(
    callback: CallbackQuery, callback_data: StudyDivisionCallbackFactory, state: FSMContext
):
    """
    Handling the study division selection, sends a keyboard with a list of study levels
    :param callback:
    :param callback_data:
    :param state:
    """
    await change_message_to_loading(callback.message)
    study_levels = await get_study_levels(callback_data.alias)
    await callback.message.delete()
    await callback.message.answer(
        text=_("⬇️ Выберите уровень подготовки:"),
        reply_markup=await create_study_levels_keyboard(study_levels),
    )
    await state.set_data({"study_levels": [level.model_dump() for level in study_levels]})


@router.callback_query(StudyLevelCallbackFactory.filter())
async def study_levels_navigation_callback(
    callback: CallbackQuery, callback_data: StudyLevelCallbackFactory, state: FSMContext
):
    """
    Handling the study level selection, sends a keyboard with a list of program combinations
    :param callback:
    :param callback_data:
    :param state:
    """
    data = await state.get_data()
    program_combinations = data["study_levels"][callback_data.serial]["program_combinations"]
    await callback.message.edit_text(
        text=_("⬇️ Выберите программу подготовки: "),
        reply_markup=await create_study_programs_keyboard(program_combinations),
    )
    await state.set_data({"program_combinations": program_combinations})


@router.callback_query(ProgramCombinationsCallbackFactory.filter())
async def admission_years_navigation_callback(
    callback: CallbackQuery, callback_data: ProgramCombinationsCallbackFactory, state: FSMContext
):
    """
    Handling the program combination selection, sends a keyboard with a list of admission years
    :param callback:
    :param callback_data:
    :param state:
    """
    data = await state.get_data()
    admission_years = data["program_combinations"][callback_data.serial]["admission_years"]
    await callback.message.edit_text(
        text=_("⬇️ Выберите год поступления: "),
        reply_markup=await create_admission_years_keyboard(admission_years),
    )
    await state.set_data({})


@router.callback_query(AdmissionYearsCallbackFactory.filter())
@flags.chat_action(ChatAction.TYPING)
async def group_choice_navigation_callback(
    callback: CallbackQuery, callback_data: AdmissionYearsCallbackFactory, state: FSMContext
):
    """
    Handling the admission year selection, sends a keyboard with a list of groups
    :param callback:
    :param callback_data:
    :param state:
    """
    await change_message_to_loading(callback.message)
    groups = await get_groups(callback_data.study_program_id)
    if len(groups) > 0:
        await callback.message.delete()
        await callback.message.answer(text=_("⬇️ Выберите группу:"), reply_markup=await create_groups_keyboard(groups))
        await state.set_state(Searching.choosing)
    else:
        await callback.message.edit_text(_("❌ По данной программе группы не найдены!"))
