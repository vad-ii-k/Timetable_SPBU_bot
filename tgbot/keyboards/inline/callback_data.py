from aiogram.utils.callback_data import CallbackData

user_status_callback = CallbackData("user_status", "name")

choice_teacher_callback = CallbackData("choice_teacher", "tt_id", "user_type")

choice_group_callback = CallbackData("choice_group", "tt_id", "user_type")

timetable_callback = CallbackData("timetable", "button")

settings_callback = CallbackData("settings", "type")

schedule_subscription_callback = CallbackData("schedule_subscription", "answer")

study_divisions_callback = CallbackData("study_divisions", "alias")

study_levels_callback = CallbackData("study_levels", "serial")

study_programs_callback = CallbackData("study_program_combinations", "serial")

admission_years_callback = CallbackData("admission_years_combinations", "program_id")

settings_daily_summary_callback = CallbackData("time", "choice")
