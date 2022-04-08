import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputFile

from keyboards.inline.callback_data import choice_teacher_callback
from keyboards.inline.choice_teacher_buttons import create_teachers_keyboard
from keyboards.inline.schedule_subscription_buttons import create_schedule_subscription_keyboard
from keyboards.inline.timetable_buttons import create_timetable_keyboard
from loader import dp, db
from states.choice_teacher import TeacherChoice
from utils.tt_api import teacher_search, teacher_timetable_week


@dp.message_handler(state=TeacherChoice.getting_choice)
async def getting_choice_for_teacher(message: types.Message):
    answer = message.text
    teachers_list = await teacher_search(answer)
    if len(teachers_list) == 0:
        await TeacherChoice.wrong_last_name.set()
        await wrong_last_name(message)
    elif len(teachers_list) > 40:
        await TeacherChoice.widespread_last_name.set()
        await widespread_last_name(message)
    else:
        answer = await message.answer("<i>Получение списка преподавателей...</i>")
        await answer.edit_text("Выберите преподавателя из списка:",
                               reply_markup=await create_teachers_keyboard(teachers_list))
        await TeacherChoice.choosing.set()


@dp.message_handler(state=TeacherChoice.choosing)
async def choosing_teacher(message: types.Message):
    await message.delete()


@dp.message_handler(state=TeacherChoice.wrong_last_name)
async def wrong_last_name(message: types.Message):
    await message.chat.delete_message(message.message_id - 1)
    await message.delete()
    await message.answer(f"Преподаватель <i>{message.text}</i> не найден!\n"
                         "Пожалуйста, введите другую фамилию:")
    await TeacherChoice.getting_choice.set()


@dp.message_handler(state=TeacherChoice.widespread_last_name)
async def widespread_last_name(message: types.Message):
    await message.chat.delete_message(message.message_id - 1)
    await message.delete()
    await message.answer(f"Фамилия <i>{message.text}</i> очень распространена\n"
                         "Попробуйте ввести фамилию и первую букву имени:")
    await TeacherChoice.getting_choice.set()


@dp.callback_query_handler(choice_teacher_callback.filter(), state=TeacherChoice.choosing)
async def viewing_schedule(query: CallbackQuery, state: FSMContext, callback_data: dict):
    await state.finish()
    await query.message.chat.delete_message(query.message.message_id - 2)
    await query.message.chat.delete_message(query.message.message_id - 1)
    await query.answer(cache_time=5)
    logging.info(f"call = {callback_data}")

    settings = await db.get_settings(query.from_user.id)
    is_picture = settings.schedule_view_is_picture
    await query.message.edit_text("<i>Получение расписания...</i>")

    text = await teacher_timetable_week(callback_data.get("teacher_id"))
    if is_picture:
        answer = await query.message.answer_photo(photo=InputFile("utils/image_converter/output.png"))
        await query.message.delete()
    else:
        answer = await query.message.edit_text(text)

    await state.update_data(user_type="teacher", tt_id=callback_data.get("teacher_id"),
                            full_name=text.split('\n', 1)[0].split(' ', 1)[1])
    await answer.edit_reply_markup(reply_markup=await create_timetable_keyboard(is_picture=is_picture))

    await answer.answer(text="Хотите сделать это расписание своим основным?",
                        reply_markup=await create_schedule_subscription_keyboard())
