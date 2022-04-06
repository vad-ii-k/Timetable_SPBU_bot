from aiogram.utils.callback_data import CallbackData

user_status_callback = CallbackData("user_status", "name")

choice_teacher_callback = CallbackData("choice_teacher", "teacher_id")

timetable_callback = CallbackData("timetable", "button")

settings_callback = CallbackData("settings", "type")

schedule_subscription_callback = CallbackData("schedule_subscription", "answer")

study_divisions_callback = CallbackData("study_divisions", "alias")

study_levels_callback = CallbackData("study_levels", "serial")

study_programs_callback = CallbackData("study_program_combinations", "serial")

admission_years_callback = CallbackData("admission_years_combinations", "program_id")

groups_callback = CallbackData("groups", "group_id")
