from datetime import date, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.cb_data import (
    StudyDivisionCallbackFactory,
    StudyLevelCallbackFactory,
    ProgramCombinationsCallbackFactory,
    AdmissionYearsCallbackFactory,
    StartMenuCallbackFactory,
    ScheduleCallbackFactory,
    TTObjectChoiceCallbackFactory,
)
from tgbot.data_classes import (
    StudyDivision,
    StudyLevel,
    ProgramCombination,
    AdmissionYear,
    GroupSearchInfo,
    EducatorSearchInfo,
)
from tgbot.misc.states import UserType


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
            callback_data=TTObjectChoiceCallbackFactory(tt_id=group.tt_id, user_type=UserType.STUDENT)
        )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_educators_keyboard(educators: list[EducatorSearchInfo]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for educator in educators:
        keyboard.button(
            text=educator.full_name,
            callback_data=TTObjectChoiceCallbackFactory(tt_id=educator.tt_id, user_type=UserType.EDUCATOR)
        )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_schedule_keyboard(
        is_photo: bool, tt_id: int, user_type: str, day_counter: int = 0
) -> InlineKeyboardMarkup:
    current_date = date.today() + timedelta(day_counter)
    prev_day_date = current_date - timedelta(days=1)
    next_day_date = current_date + timedelta(days=1)

    timetable_keyboard = InlineKeyboardBuilder()
    prev_day_button = InlineKeyboardButton(
        text=f"⬅ {prev_day_date:%d.%m}",
        callback_data=ScheduleCallbackFactory(button="1-1", tt_id=tt_id, user_type=user_type).pack(),
    )
    today_button = InlineKeyboardButton(
        text="Сегодня",
        callback_data=ScheduleCallbackFactory(button="1-2", tt_id=tt_id, user_type=user_type).pack(),
    )
    next_day_button = InlineKeyboardButton(
        text=f"{next_day_date:%d.%m} ➡️",
        callback_data=ScheduleCallbackFactory(button="1-3", tt_id=tt_id, user_type=user_type).pack(),
    )
    if day_counter > -7:
        timetable_keyboard.row(prev_day_button, today_button, next_day_button)
    else:
        timetable_keyboard.row(today_button, next_day_button)

    this_week_button = InlineKeyboardButton(
        text="⏹ Эта неделя",
        callback_data=ScheduleCallbackFactory(button="2-1", tt_id=tt_id, user_type=user_type).pack(),
    )
    next_week_button = InlineKeyboardButton(
        text="След. неделя ⏩",
        callback_data=ScheduleCallbackFactory(button="2-2", tt_id=tt_id, user_type=user_type).pack(),
    )
    timetable_keyboard.row(this_week_button, next_week_button)

    schedule_view = InlineKeyboardButton(
        text="📝 Текстом 📝" if is_photo else "🖼 Картинкой 🖼",
        callback_data=ScheduleCallbackFactory(button="3-1", tt_id=tt_id, user_type=user_type).pack(),
    )
    timetable_keyboard.row(schedule_view)

    return timetable_keyboard.as_markup()
