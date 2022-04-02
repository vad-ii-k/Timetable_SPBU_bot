from aiogram.utils.callback_data import CallbackData

user_status_callback = CallbackData("user_status", "name")

choice_teacher_callback = CallbackData("choice_teacher", "Id")

timetable_callback = CallbackData("timetable", "button", "type", "Id")

settings_callback = CallbackData("settings", "type")

study_divisions_callback = CallbackData("study_divisions", "alias")

study_levels_callback = CallbackData("study_levels", "serial")

study_programs_callback = CallbackData("study_program_combinations", "serial")

admission_years_callback = CallbackData("admission_years_combinations", "program_id")

groups_callback = CallbackData("groups", "group_id")
