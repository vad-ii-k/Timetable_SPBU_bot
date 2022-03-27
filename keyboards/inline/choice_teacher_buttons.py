import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import choice_teacher_callback


async def create_teachers_keyboard(teachers: list):
    choice_teacher = InlineKeyboardMarkup(row_width=1)
    for teacher in teachers:
        button = InlineKeyboardButton(text=teacher["FullName"], callback_data=choice_teacher_callback.new(
            Id=teacher["Id"]
        ))
        choice_teacher.insert(button)
    return choice_teacher
