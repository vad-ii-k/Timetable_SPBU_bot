"""
States for the [Finite State Machine](https://docs.aiogram.dev/en/dev-3.x/dispatcher/finite_state_machine/index.html)
"""

from aiogram.fsm.state import State, StatesGroup


class Searching(StatesGroup):
    """States to search for a group or teacher"""

    getting_group_choice = State()
    """ Status of getting the list of groups """
    getting_educator_choice = State()
    """ Status of getting the list of educators """
    choosing = State()
    """ Status of selecting a group or teacher from the list """
