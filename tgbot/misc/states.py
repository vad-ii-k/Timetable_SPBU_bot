from enum import Enum

from aiogram.fsm.state import StatesGroup, State


class SearchEducator(StatesGroup):
    getting_choice = State()
    choosing = State()
    wrong_last_name = State()
    widespread_last_name = State()


class UserType(str, Enum):
    STUDENT = "student"
    EDUCATOR = "educator"
