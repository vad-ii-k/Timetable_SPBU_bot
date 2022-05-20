import logging
from contextlib import suppress

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound

from tgbot.handlers.users.helpers import send_schedule
from tgbot.keyboards.inline.callback_data import choice_teacher_callback
from tgbot.keyboards.inline.choice_teacher_buttons import create_teachers_keyboard
from tgbot.loader import dp
from tgbot.states.choice_teacher import TeacherChoice
from utils.timetable.api import teacher_search


@dp.message_handler(state=TeacherChoice.getting_choice)
async def getting_choice_for_teacher(message: types.Message) -> None:
    answer = message.text
    answer_msg = await message.answer("⏳")
    teachers_list = await teacher_search(answer)
    if len(teachers_list) == 0:
        await TeacherChoice.wrong_last_name.set()
        await wrong_last_name(message)
    elif len(teachers_list) > 50:
        await TeacherChoice.widespread_last_name.set()
        await widespread_last_name(message)
    else:
        await answer_msg.edit_text("Выберите преподавателя из списка:")
        await answer_msg.edit_reply_markup(
            reply_markup=await create_teachers_keyboard(teachers_list)
        )
        await TeacherChoice.choosing.set()


@dp.message_handler(state=TeacherChoice.choosing)
async def choosing_teacher(message: types.Message) -> None:
    await message.delete()


@dp.message_handler(state=TeacherChoice.wrong_last_name)
async def wrong_last_name(message: types.Message) -> None:
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.chat.delete_message(message.message_id - 1)
        await message.delete()
        await message.chat.delete_message(message.message_id + 1)
    await message.answer(
        f"Преподаватель \"<i>{message.text.replace('>', '').replace('<', '')}</i>\" не найден!\n"
        "Пожалуйста, введите другую фамилию:"
    )
    await TeacherChoice.getting_choice.set()


@dp.message_handler(state=TeacherChoice.widespread_last_name)
async def widespread_last_name(message: types.Message) -> None:
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.chat.delete_message(message.message_id - 1)
        await message.delete()
        await message.chat.delete_message(message.message_id + 1)
    await message.answer(
        f'Фамилия "<i>{message.text}</i>" очень распространена\n'
        "Попробуйте ввести фамилию и первую букву имени:"
    )
    await TeacherChoice.getting_choice.set()


@dp.callback_query_handler(choice_teacher_callback.filter(), state=TeacherChoice.choosing)
async def teacher_viewing_schedule_handler(
        query: CallbackQuery, state: FSMContext, callback_data: dict
) -> None:
    await state.finish()
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await query.message.chat.delete_message(query.message.message_id - 2)
        await query.message.chat.delete_message(query.message.message_id - 1)
    await query.answer(cache_time=1)
    logging.info("call = %s", callback_data)

    await send_schedule(query.message, callback_data, state, subscription=True)
