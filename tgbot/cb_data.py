from aiogram.filters.callback_data import CallbackData

from tgbot.data_classes import ProgramCombination


class StudyDivisionCallbackFactory(CallbackData, prefix="study_division"):
    alias: str


class StudyLevelCallbackFactory(CallbackData, prefix="study_level"):
    serial: int


class ProgramCombinationsCallbackFactory(CallbackData, prefix="program_combinations"):
    serial: int


class AdmissionYearsCallbackFactory(CallbackData, prefix="admission_years"):
    study_program_id: str


class GroupChoiceCallbackFactory(CallbackData, prefix="admission_years"):
    tt_id: str
