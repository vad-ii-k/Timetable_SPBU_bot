from aiogram.filters.callback_data import CallbackData


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


class GroupChoiceCallbackFactory(CallbackData, prefix="group_choice"):
    tt_id: str


class EducatorChoiceCallbackFactory(CallbackData, prefix="educator_choice"):
    tt_id: str
