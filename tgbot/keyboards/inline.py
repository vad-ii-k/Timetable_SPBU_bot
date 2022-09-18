from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.cb_data import (
    StudyDivisionCallbackFactory,
    StudyLevelCallbackFactory,
    ProgramCombinationsCallbackFactory,
    AdmissionYearsCallbackFactory,
    GroupChoiceCallbackFactory,
    StartMenuCallbackFactory,
    EducatorChoiceCallbackFactory,
)
from tgbot.data_classes import (
    StudyDivision,
    StudyLevel,
    ProgramCombination,
    AdmissionYear,
    GroupSearchInfo,
    EducatorSearchInfo,
)


async def create_start_choice_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="Названию группы",
        callback_data=StartMenuCallbackFactory(type="student_search")
    )
    keyboard.button(
        text="Навигации по программам",
        callback_data=StartMenuCallbackFactory(type="student_navigation")
    )
    keyboard.button(
        text="ФИО преподавателя",
        callback_data=StartMenuCallbackFactory(type="educator_search")
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_study_divisions_keyboard(study_divisions: list[StudyDivision]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for division in study_divisions:
        keyboard.button(
            text=division.name,
            callback_data=StudyDivisionCallbackFactory(alias=division.alias)
        )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_study_levels_keyboard(study_levels: list[StudyLevel]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for serial, level in enumerate(study_levels):
        keyboard.button(
            text=level.name,
            callback_data=StudyLevelCallbackFactory(serial=serial)
        )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_study_programs_keyboard(program_combinations: list[ProgramCombination]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for serial, program in enumerate(program_combinations):
        keyboard.button(
            text=program.name,
            callback_data=ProgramCombinationsCallbackFactory(serial=serial)
        )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_admission_years_keyboard(admission_years: list[AdmissionYear]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for year in admission_years:
        keyboard.button(
            text=year.year,
            callback_data=AdmissionYearsCallbackFactory(study_program_id=year.study_program_id)
        )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_groups_keyboard(groups: list[GroupSearchInfo]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for group in groups:
        keyboard.button(
            text=group.name,
            callback_data=GroupChoiceCallbackFactory(tt_id=group.tt_id)
        )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_educators_keyboard(educators: list[EducatorSearchInfo]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for educator in educators:
        keyboard.button(
            text=educator.full_name,
            callback_data=EducatorChoiceCallbackFactory(tt_id=educator.tt_id)
        )
    keyboard.adjust(1)
    return keyboard.as_markup()
