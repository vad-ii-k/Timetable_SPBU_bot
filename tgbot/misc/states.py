from enum import Enum

from aiogram.fsm.state import StatesGroup, State


class Searching(StatesGroup):
    getting_group_choice = State()
    getting_educator_choice = State()
    choosing = State()


class UserType(str, Enum):
    STUDENT = "student"
    EDUCATOR = "educator"
