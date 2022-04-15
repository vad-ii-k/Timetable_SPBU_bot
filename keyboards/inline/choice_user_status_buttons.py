from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import user_status_callback


choice_user_status = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Названию группы", callback_data=user_status_callback.new(
                name="student group"
            ))
        ],
        [
            InlineKeyboardButton(text="Навигации по программам", callback_data=user_status_callback.new(
                name="student navigation"
            ))
        ],
        [
            InlineKeyboardButton(text="ФИО преподавателя", callback_data=user_status_callback.new(
                name="teacher"
            ))
        ]
    ]
)
