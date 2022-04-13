from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import choice_group_callback
from utils.db_api.db_models import Group


async def create_choice_groups_keyboard(groups: list) -> InlineKeyboardMarkup:
    choice_group = InlineKeyboardMarkup(row_width=1)
    group: Group
    for group in groups:
        button = InlineKeyboardButton(text=group.name, callback_data=choice_group_callback.new(
            group_id=group.tt_id
        ))
        choice_group.insert(button)
    return choice_group
