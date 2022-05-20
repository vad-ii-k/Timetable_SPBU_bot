from typing import List, Dict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.inline.callback_data import study_divisions_callback, \
    study_levels_callback, study_programs_callback, admission_years_callback, choice_group_callback


async def create_study_divisions_keyboard(divisions: List[Dict[str, str]]) -> InlineKeyboardMarkup:
    study_divisions_keyboard = InlineKeyboardMarkup(row_width=1)
    for division in divisions:
        button = InlineKeyboardButton(
            text=division["Name"],
            callback_data=study_divisions_callback.new(alias=division["Alias"]),
        )
        study_divisions_keyboard.insert(button)
    return study_divisions_keyboard


async def create_study_levels_keyboard(levels: List[Dict[str, str]]) -> InlineKeyboardMarkup:
    study_levels_keyboard = InlineKeyboardMarkup(row_width=1)
    for level in levels:
        button = InlineKeyboardButton(
            text=level["StudyLevelName"],
            callback_data=study_levels_callback.new(serial=level["Serial"]),
        )
        study_levels_keyboard.insert(button)
    return study_levels_keyboard


async def create_study_programs_keyboard(programs: List[Dict[str, str]]) -> InlineKeyboardMarkup:
    study_programs_keyboard = InlineKeyboardMarkup(row_width=1)
    for program in programs:
        button = InlineKeyboardButton(
            text=program["Name"],
            callback_data=study_programs_callback.new(serial=program["Serial"]),
        )
        study_programs_keyboard.insert(button)
    return study_programs_keyboard


async def create_admission_years_keyboard(years: List[Dict[str, str]]) -> InlineKeyboardMarkup:
    admission_years_keyboard = InlineKeyboardMarkup(row_width=2)
    for year in years:
        button = InlineKeyboardButton(
            text=year["Year"],
            callback_data=admission_years_callback.new(program_id=year["StudyProgramId"])
        )
        admission_years_keyboard.insert(button)
    return admission_years_keyboard


async def create_groups_keyboard(groups: List[Dict[str, str]]) -> InlineKeyboardMarkup:
    groups_keyboard = InlineKeyboardMarkup(row_width=1)
    for group in groups:
        button = InlineKeyboardButton(
            text=group["StudentGroupName"],
            callback_data=choice_group_callback.new(
                tt_id=group["StudentGroupId"], user_type="student"
            )
        )
        groups_keyboard.insert(button)
    return groups_keyboard
