""" [Inline Keyboards](https://docs.aiogram.dev/en/dev-3.x/utils/keyboard.html#inline-keyboard) """

from datetime import date, datetime, time, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.misc.cb_data import (
    AdmissionYearsCallbackFactory,
    ProgramCombinationsCallbackFactory,
    ProgramsPageCallbackFactory,
    ScheduleCallbackFactory,
    ScheduleSubscriptionCallbackFactory,
    SettingsCallbackFactory,
    SettingsDailySummaryCallbackFactory,
    StartMenuCallbackFactory,
    StudyDivisionCallbackFactory,
    StudyLevelCallbackFactory,
    TTObjectChoiceCallbackFactory,
)
from tgbot.services.db_api.db_models import Settings
from tgbot.services.schedule.data_classes import (
    EducatorSearchInfo,
    GroupSearchInfo,
    StudyDivision,
    StudyLevel,
    UserType,
)

# Лимит Telegram на reply_markup; длинные названия программ бакалавриата иначе не влезают
PROGRAMS_PAGE_SIZE = 12
BUTTON_TEXT_MAX_LEN = 60


async def create_start_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Creating a keyboard for the start menu
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=_("Названию группы"), callback_data=StartMenuCallbackFactory(type="student_search"))
    keyboard.button(
        text=_("Навигации по программам"),
        callback_data=StartMenuCallbackFactory(type="student_navigation"),
    )
    keyboard.button(text=_("ФИО преподавателя"), callback_data=StartMenuCallbackFactory(type="educator_search"))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_study_divisions_keyboard(
    study_divisions: list[StudyDivision],
) -> InlineKeyboardMarkup:
    """
    Creating a keyboard with a list of study divisions
    :param study_divisions:
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    for division in study_divisions:
        keyboard.button(text=division.name, callback_data=StudyDivisionCallbackFactory(alias=division.alias))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_study_levels_keyboard(study_levels: list[StudyLevel]) -> InlineKeyboardMarkup:
    """
    Creating a keyboard with a list of study levels
    :param study_levels:
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    for serial, level in enumerate(study_levels):
        keyboard.button(text=level.name, callback_data=StudyLevelCallbackFactory(serial=serial))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_study_programs_keyboard(
    program_combinations: list[dict[str, str]],
    page: int = 0,
) -> InlineKeyboardMarkup:
    """
    Creating a keyboard with a list of program combinations
    :param program_combinations:
    :param page: страница списка (пагинация из‑за лимита reply markup)
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    total = len(program_combinations)
    total_pages = max(1, (total + PROGRAMS_PAGE_SIZE - 1) // PROGRAMS_PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    start = page * PROGRAMS_PAGE_SIZE
    page_items = program_combinations[start : start + PROGRAMS_PAGE_SIZE]

    for serial, program in enumerate(page_items, start=start):
        name = program["name"]
        if len(name) > BUTTON_TEXT_MAX_LEN:
            name = name[: BUTTON_TEXT_MAX_LEN - 1] + "…"
        keyboard.button(
            text=name,
            callback_data=ProgramCombinationsCallbackFactory(serial=serial),
        )

    row_sizes = [1] * len(page_items)
    if total_pages > 1:
        if page > 0:
            keyboard.button(text="⬅️", callback_data=ProgramsPageCallbackFactory(page=page - 1))
        keyboard.button(
            text=f"{page + 1}/{total_pages}",
            callback_data=ProgramsPageCallbackFactory(page=page),
        )
        if page < total_pages - 1:
            keyboard.button(text="➡️", callback_data=ProgramsPageCallbackFactory(page=page + 1))
        row_sizes.append(1 + (page > 0) + (page < total_pages - 1))

    if row_sizes:
        keyboard.adjust(*row_sizes)
    return keyboard.as_markup()


async def create_admission_years_keyboard(admission_years: list[dict[str, str]]) -> InlineKeyboardMarkup:
    """
    Creating a keyboard with a list of admission years
    :param admission_years:
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    for year in admission_years:
        keyboard.button(
            text=year["year"],
            callback_data=AdmissionYearsCallbackFactory(study_program_id=year["study_program_id"]),
        )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_groups_keyboard(groups: list[GroupSearchInfo]) -> InlineKeyboardMarkup:
    """
    Creating a keyboard with a list of groups
    :param groups:
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    for group in groups:
        keyboard.button(
            text=group.name,
            callback_data=TTObjectChoiceCallbackFactory(tt_id=group.tt_id, user_type=UserType.STUDENT),
        )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_educators_keyboard(educators: list[EducatorSearchInfo]) -> InlineKeyboardMarkup:
    """
    Creating a keyboard with a list of educators
    :param educators:
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    for educator in educators:
        keyboard.button(
            text=educator.full_name,
            callback_data=TTObjectChoiceCallbackFactory(tt_id=educator.tt_id, user_type=UserType.EDUCATOR),
        )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def create_schedule_keyboard(is_photo: bool, callback_data: ScheduleCallbackFactory) -> InlineKeyboardMarkup:
    """
    Creating a keyboard for a schedule
    :param is_photo: current schedule view
    :param callback_data:
    :return:
    """
    day_counter = 0 if callback_data.day_counter is None else callback_data.day_counter
    current_date = date.today() + timedelta(day_counter)
    prev_day_date = current_date - timedelta(days=1)
    next_day_date = current_date + timedelta(days=1)

    text_of_buttons = [
        f"⬅ {prev_day_date:%d.%m}",
        _("Сегодня"),
        f"{next_day_date:%d.%m} ➡️",
        _("⏹ Эта неделя"),
        _("След. неделя ⏩"),
        _("📝 Текстом 📝") if is_photo else _("🖼 Картинкой 🖼"),
    ]
    button_ids = ["1-1", "1-2", "1-3", "2-1", "2-2", "3-1"]

    keyboard = InlineKeyboardBuilder()
    for button_text, button_id in zip(text_of_buttons, button_ids):
        keyboard.button(
            text=button_text,
            callback_data=ScheduleCallbackFactory(
                button=button_id,
                tt_id=callback_data.tt_id,
                user_type=callback_data.user_type,
                day_counter=callback_data.day_counter,
                week_counter=callback_data.week_counter,
            ).pack(),
        )
    keyboard.adjust(3, 2, 1)
    return keyboard.as_markup()


async def create_settings_keyboard(settings: Settings) -> InlineKeyboardMarkup:
    """
    Creating a keyboard for settings
    :param settings: current user settings
    :return:
    """
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
    text += "🇷🇺" if settings.language == "ru" else "🇬🇧"
    language = InlineKeyboardButton(text=text, callback_data=SettingsCallbackFactory(type="language").pack())
    settings_keyboard.row(language)
    return settings_keyboard.as_markup()


async def create_settings_daily_summary_keyboard(selected_option: datetime) -> InlineKeyboardMarkup:
    """
    Creating a keyboard to change the parameters of the daily summary
    :param selected_option: current time for the daily summary
    :return:
    """
    daily_summary_keyboard = InlineKeyboardBuilder()

    suggested_time = [(19, "🕖"), (7, "🕖"), (20, "🕗"), (8, "🕗"), (21, "🕘"), (9, "🕘")]
    for option, sticker in suggested_time:
        daily_summary_keyboard.button(
            text=f"{'●' if selected_option is not None and option == selected_option.hour else '○'}"
            f" {option}:00 {sticker}",
            callback_data=SettingsDailySummaryCallbackFactory(choice=str(option)),
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


async def create_schedule_subscription_keyboard() -> InlineKeyboardMarkup:
    """
    Creating a keyboard for a schedule subscription question
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=_("Да, сделать основным ✅"),
        callback_data=ScheduleSubscriptionCallbackFactory(answer=True),
    )
    keyboard.button(
        text=_("Нет, только посмотреть ❌"),
        callback_data=ScheduleSubscriptionCallbackFactory(answer=False),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
