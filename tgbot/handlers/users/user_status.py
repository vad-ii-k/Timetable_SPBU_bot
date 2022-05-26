import logging

from aiogram.types import CallbackQuery

from tgbot.handlers.users.helpers import change_message_to_progress
from tgbot.keyboards.inline.callback_data import user_status_callback
from tgbot.keyboards.inline.student_navigaton_buttons import create_study_divisions_keyboard
from tgbot.loader import dp
from tgbot.states.choice_group import GroupChoice
from tgbot.states.choice_teacher import TeacherChoice
from utils.timetable.api import get_study_divisions


@dp.callback_query_handler(user_status_callback.filter(name="student group"))
async def student_group_search_handler(query: CallbackQuery, callback_data: dict) -> None:
    await query.answer(cache_time=1)
    logging.info("call = %s", callback_data)
    await query.message.edit_text("Введите название группы:\n *<i>например, 20.Б09-мм</i>")
    await GroupChoice.getting_choice.set()


@dp.callback_query_handler(user_status_callback.filter(name="student navigation"))
async def student_navigation_handler(query: CallbackQuery, callback_data: dict) -> None:
    await query.answer(cache_time=1)
    logging.info("call = %s", callback_data)
    await change_message_to_progress(query.message, False)
    study_divisions = await get_study_divisions()
    await query.message.edit_text("Выберите направление: ")
    await query.message.edit_reply_markup(
        reply_markup=await create_study_divisions_keyboard(study_divisions)
    )


@dp.callback_query_handler(user_status_callback.filter(name="teacher"))
async def teacher_search_handler(query: CallbackQuery, callback_data: dict) -> None:
    await query.answer(cache_time=1)
    logging.info("call = %s", callback_data)
    await query.message.edit_text("Введите Вашу фамилию:")
    await TeacherChoice.getting_choice.set()
