from aiogram.dispatcher.filters.state import StatesGroup, State


class GroupChoice(StatesGroup):
    getting_choice = State()
    choosing = State()
    wrong_group = State()
    too_many_groups = State()
