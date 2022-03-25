import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.inline.callback_data import choice_teacher_callback
from keyboards.inline.choice_teacher_buttons import create_teachers_keyboard
from loader import dp
from states.choice_teacher import TeacherChoice
from utils.tt_api import teacher_search


@dp.message_handler(state=TeacherChoice.getting_choice)
async def getting_choice_for_teacher(message: types.Message):
    answer = message.text
    teachers_list = await teacher_search(answer)
    if len(teachers_list) == 0:
        await TeacherChoice.wrong_last_name.set()
        await other_last_name(message)
    elif len(teachers_list) > 40:
        pass
        # TODO
    else:
        await message.answer("Выберите преподавателя из списка:",
                                      reply_markup=await create_teachers_keyboard(teachers_list))
        await TeacherChoice.choosing.set()


@dp.message_handler(state=TeacherChoice.choosing)
async def choosing_teacher(message: types.Message):
    await message.delete()


@dp.message_handler(state=TeacherChoice.wrong_last_name)
async def other_last_name(message: types.Message):
    await message.chat.delete_message(message.message_id - 1)
    await message.delete()
    await message.answer(f"Преподавателя с фамилией {message.text} нет!\n"
                         "Пожалуйста, введите другую:")
    await TeacherChoice.getting_choice.set()


@dp.callback_query_handler(choice_teacher_callback.filter(), state=TeacherChoice.choosing)
async def handling_group_of_student(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.answer(cache_time=60)
    callback_data = call.data
    logging.info(f"call = {callback_data}")

    await call.message.edit_text(f"{callback_data}")
