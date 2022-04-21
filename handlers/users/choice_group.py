import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from handlers.users.helpers import send_group_schedule
from keyboards.inline.callback_data import choice_group_callback
from keyboards.inline.choice_group_buttons import create_choice_groups_keyboard
from loader import dp, db
from states.choice_group import GroupChoice


@dp.message_handler(state=GroupChoice.getting_choice)
async def getting_choice_for_student(message: types.Message):
    groups_list = await db.get_groups_by_name(message.text)
    if len(groups_list) > 0:
        answer_msg = await message.answer("Выберите группу из списка:")
        await answer_msg.edit_reply_markup(reply_markup=await create_choice_groups_keyboard(groups_list))
        await GroupChoice.choosing.set()
    else:
        await GroupChoice.wrong_group.set()
        await groups_not_found_handler(message)


@dp.message_handler(state=GroupChoice.wrong_group)
async def groups_not_found_handler(message: Message):
    await message.chat.delete_message(message.message_id - 1)
    await message.delete()
    await message.answer(f"Группа <i>{message.text}</i> не найдена!\n"
                         "Попробуйте ещё раз или воспользуйтесь навигацией:")
    await GroupChoice.getting_choice.set()


@dp.callback_query_handler(choice_group_callback.filter(), state=GroupChoice.choosing)
async def group_viewing_schedule_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.finish()
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")
    await send_group_schedule(query, callback_data, state)