import logging

from aiogram.types import CallbackQuery

from keyboards.inline.callback_data import user_status_callback
from keyboards.inline.student_navigaton_buttons import create_study_divisions_keyboard
from loader import dp
from states.choice_group import GroupChoice
from states.choice_teacher import TeacherChoice
from utils.tt_api import get_study_divisions


@dp.callback_query_handler(user_status_callback.filter(name="student group"))
async def student_group_search_handler(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=5)
    logging.info(f"call = {callback_data}")
    await query.message.edit_text("Введите название группы:\n*<i>например, 20.Б09-мм</i>")
    await GroupChoice.getting_choice.set()


@dp.callback_query_handler(user_status_callback.filter(name="student navigation"))
async def student_navigation_handler(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=5)
    logging.info(f"call = {callback_data}")
    await call.message.edit_text("Выберите направление: ")
    study_divisions = await get_study_divisions()
    await call.message.edit_reply_markup(reply_markup=await create_study_divisions_keyboard(study_divisions))


@dp.callback_query_handler(user_status_callback.filter(name="teacher"))
async def teacher_search_handler(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=5)
    logging.info(f"call = {callback_data}")
    await query.message.edit_text("Введите Вашу фамилию:")
    await TeacherChoice.getting_choice.set()
