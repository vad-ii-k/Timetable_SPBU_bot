from typing import List, Dict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.inline.callback_data import choice_teacher_callback


async def create_teachers_keyboard(teachers: List[Dict[str, str]]) -> InlineKeyboardMarkup:
    choice_teacher = InlineKeyboardMarkup(row_width=1)
    for teacher in teachers:
        button = InlineKeyboardButton(
            text=teacher["FullName"],
            callback_data=choice_teacher_callback.new(tt_id=teacher["Id"], user_type='teacher')
        )
        choice_teacher.insert(button)
    return choice_teacher
