from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import user_status_callback

choice_user_status = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Я студент (знаю название группы)", callback_data=user_status_callback.new(
                name="student group"
            ))
        ],
        [
            InlineKeyboardButton(text="Я студент (не знаю название группы)", callback_data=user_status_callback.new(
                name="student navigation"
            ))
        ],
        [
            InlineKeyboardButton(text="Я преподаватель", callback_data=user_status_callback.new(
                name="teacher"
            ))
        ]
    ]
)
