import logging

from aiogram.types import CallbackQuery

from keyboards.inline.callback_data import user_status_callback
from loader import dp
from states.choice_teacher import TeacherChoice


@dp.callback_query_handler(user_status_callback.filter(name="student group"))
async def handling_group_of_student(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = call.data
    logging.info(f"call = {callback_data}")

    await call.message.edit_text("Введите название группы:\n"
                                 "*<i>например, 20Б.09-мм</i>")


@dp.callback_query_handler(user_status_callback.filter(name="student navigation"))
async def handling_group_of_student(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = call.data
    logging.info(f"call = {callback_data}")

    await call.message.answer("Здесь будет выбор по кнопочкам")


@dp.callback_query_handler(user_status_callback.filter(name="teacher"), state=None)
async def handling_group_of_student(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = call.data
    logging.info(f"call = {callback_data}")

    await call.message.edit_text("Введите Вашу фамилию:")

    await TeacherChoice.getting_choice.set()
