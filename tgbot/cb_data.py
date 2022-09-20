from aiogram.filters.callback_data import CallbackData

from tgbot.misc.states import UserType


class StartMenuCallbackFactory(CallbackData, prefix="start_menu"):
    type: str


class StudyDivisionCallbackFactory(CallbackData, prefix="study_division"):
    alias: str


class StudyLevelCallbackFactory(CallbackData, prefix="study_level"):
    serial: int


class ProgramCombinationsCallbackFactory(CallbackData, prefix="program_combinations"):
    serial: int


class AdmissionYearsCallbackFactory(CallbackData, prefix="admission_years"):
    study_program_id: str


class TTObjectChoiceCallbackFactory(CallbackData, prefix="timetable_object_choice"):
    tt_id: str
    user_type: UserType


class ScheduleCallbackFactory(CallbackData, prefix="schedule"):
    tt_id: int
    user_type: UserType
    button: str
    day_counter: int | None
    week_counter: int | None
