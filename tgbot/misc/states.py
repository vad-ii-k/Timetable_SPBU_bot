from enum import Enum

from aiogram.fsm.state import StatesGroup, State


class SearchEducator(StatesGroup):
    getting_choice = State()
    choosing = State()


class SearchGroup(StatesGroup):
    getting_choice = State()
    choosing = State()


class UserType(str, Enum):
    STUDENT = "student"
    EDUCATOR = "educator"
