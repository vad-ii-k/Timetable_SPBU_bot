from datetime import date, timedelta, time, datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.cb_data import (
    StudyDivisionCallbackFactory,
    StudyLevelCallbackFactory,
    ProgramCombinationsCallbackFactory,
    AdmissionYearsCallbackFactory,
    StartMenuCallbackFactory,
    ScheduleCallbackFactory,
    TTObjectChoiceCallbackFactory, SettingsCallbackFactory, SettingsDailySummaryCallbackFactory,
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
from tgbot.services.db_api.db_models import Settings


async def create_start_choice_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=_("Названию группы"), callback_data=StartMenuCallbackFactory(type="student_search")
    )
    keyboard.button(
        text=_("Навигации по программам"), callback_data=StartMenuCallbackFactory(type="student_navigation")
    )
    keyboard.button(
        text=_("ФИО преподавателя"), callback_data=StartMenuCallbackFactory(type="educator_search")
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_study_divisions_keyboard(study_divisions: list[StudyDivision]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for division in study_divisions:
        keyboard.button(text=division.name, callback_data=StudyDivisionCallbackFactory(alias=division.alias))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_study_levels_keyboard(study_levels: list[StudyLevel]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for serial, level in enumerate(study_levels):
        keyboard.button(text=level.name, callback_data=StudyLevelCallbackFactory(serial=serial))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_study_programs_keyboard(program_combinations: list[ProgramCombination]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for serial, program in enumerate(program_combinations):
        keyboard.button(text=program.name, callback_data=ProgramCombinationsCallbackFactory(serial=serial))
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
        text=_("Сегодня"),
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
        text=_("⏹ Эта неделя"),
        callback_data=ScheduleCallbackFactory(button="2-1", tt_id=tt_id, user_type=user_type).pack(),
    )
    next_week_button = InlineKeyboardButton(
        text=_("След. неделя ⏩"),
        callback_data=ScheduleCallbackFactory(button="2-2", tt_id=tt_id, user_type=user_type).pack(),
    )
    timetable_keyboard.row(this_week_button, next_week_button)

    schedule_view = InlineKeyboardButton(
        text=_("📝 Текстом 📝") if is_photo else _("🖼 Картинкой 🖼"),
        callback_data=ScheduleCallbackFactory(button="3-1", tt_id=tt_id, user_type=user_type).pack(),
    )
    timetable_keyboard.row(schedule_view)

    return timetable_keyboard.as_markup()


async def create_settings_keyboard(settings: Settings):
    settings_keyboard = InlineKeyboardBuilder()
    text = _("Присылать сводку ")
    if settings.daily_summary is None:
        text += _("на день: 🔇")
    else:
        if settings.daily_summary > time(12):
            text += _("за день до: в ")
        else:
            text += _("день в день: в ")
        text += settings.daily_summary.strftime("%H:%M")
    daily_summary = InlineKeyboardButton(text=text, callback_data=SettingsCallbackFactory(type="daily_summary").pack())
    settings_keyboard.row(daily_summary)

    text = _("Вид расписания по умолчанию: ")
    text += "🖼" if settings.schedule_view_is_picture else "📝"
    schedule_view = InlineKeyboardButton(text=text, callback_data=SettingsCallbackFactory(type="schedule_view").pack())
    settings_keyboard.row(schedule_view)

    text = _("Язык: ")
    text += "🇷🇺" if settings.language == 'ru' else "🇬🇧"
    language = InlineKeyboardButton(text=text, callback_data=SettingsCallbackFactory(type="language").pack())
    settings_keyboard.row(language)
    return settings_keyboard.as_markup()


async def create_settings_daily_summary_keyboard(selected_option: datetime):
    daily_summary_keyboard = InlineKeyboardBuilder()

    suggested_time = [(19, "🕖"), (7, "🕖"), (20, "🕗"), (8, "🕗"), (21, "🕘"), (9, "🕘")]
    for option, sticker in suggested_time:
        daily_summary_keyboard.button(
            text=f"{'●' if selected_option is not None and option == selected_option.hour else '○'}"
                 f" {option}:00 {sticker}",
            callback_data=SettingsDailySummaryCallbackFactory(choice=option),
        )
    daily_summary_keyboard.adjust(2)
    disabling_button = InlineKeyboardButton(
        text=("●" if (selected_option is None) else "○") + _(" Не присылать 🔇"),
        callback_data=SettingsDailySummaryCallbackFactory(choice="disabling").pack(),
    )
    daily_summary_keyboard.row(disabling_button)
    back_button = InlineKeyboardButton(
        text=_("Назад ↩️"),
        callback_data=SettingsDailySummaryCallbackFactory(choice="back").pack(),
    )
    daily_summary_keyboard.row(back_button)
    return daily_summary_keyboard.as_markup()
