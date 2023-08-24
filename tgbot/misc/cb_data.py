"""
[Callback Data Factory](https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/callback_data.html) classes
for processing clicks on inline keyboards
"""
from typing import Literal

from aiogram.filters.callback_data import CallbackData

from tgbot.services.schedule.data_classes import UserType


class StartMenuCallbackFactory(CallbackData, prefix="start_menu"):
    """CallbackFactory to process the welcome menu"""

    type: Literal["student_search", "student_navigation", "educator_search"]
    """ Button type """


class StudyDivisionCallbackFactory(CallbackData, prefix="study_division"):
    """CallbackFactory to process the selection of the study division"""

    alias: str
    """ Study division alias """


class StudyLevelCallbackFactory(CallbackData, prefix="study_level"):
    """CallbackFactory to process the selection of the study level"""

    serial: int
    """ Serial number of the selected study level """


class ProgramCombinationsCallbackFactory(CallbackData, prefix="program_combinations"):
    """CallbackFactory to process the selection of the study program combinations"""

    serial: int
    """ Serial number of the selected study program combinations """


class AdmissionYearsCallbackFactory(CallbackData, prefix="admission_years"):
    """CallbackFactory to process the selection of the admission year"""

    study_program_id: int
    """ Study program ID number of the selected admission year """


class TTObjectChoiceCallbackFactory(CallbackData, prefix="timetable_object_choice"):
    """CallbackFactory to process the selection of the timetable.spbu.ru object (group or educator)"""

    tt_id: int
    """ Timetable object id """
    user_type: UserType
    """ Type of timetable object (*student or educator*) """


class ScheduleCallbackFactory(CallbackData, prefix="schedule"):
    """CallbackFactory to process the selection of the schedule with different parameters"""

    tt_id: int
    """ Timetable object id """
    user_type: UserType
    """ Type of timetable object (*student or educator*) """
    button: Literal["1-1", "1-2", "1-3", "2-1", "2-2", "3-1"] | None = None
    """
    Button id

    (*None when the schedule is received without pressing the schedule keyboard buttons*)
    """
    day_counter: int | None = None
    """
    Day counter relative to the current date

    (*None when the schedule is received without pressing the schedule keyboard buttons*)
    """
    week_counter: int | None = 0
    """
    Week counter relative to the current date

    (*None when the schedule is received without pressing the schedule keyboard buttons*)
    """


class SettingsCallbackFactory(CallbackData, prefix="settings"):
    """CallbackFactory to process the main settings menu"""

    type: Literal["daily_summary", "schedule_view", "language"]
    """ Button type """


class SettingsDailySummaryCallbackFactory(CallbackData, prefix="settings_daily_summary"):
    """CallbackFactory to process the daily summary settings menu"""

    choice: str
    """ User's choice (*time* to receive the summary, *back* or *disabling* notifications buttons) """


class ScheduleSubscriptionCallbackFactory(CallbackData, prefix="schedule_subscription"):
    """CallbackFactory to process a schedule subscription"""

    answer: bool
    """ If true, then the row in the main_schedule_info table is changed """
