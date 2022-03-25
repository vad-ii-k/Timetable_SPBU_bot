from aiogram.dispatcher.filters.state import StatesGroup, State


class TeacherChoice(StatesGroup):
    getting_choice = State()
    choosing = State()
    wrong_last_name = State()
    widespread_last_name = State()
