import logging
from contextlib import suppress

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted

from tgbot.handlers.users.helpers import send_schedule
from tgbot.keyboards.inline.callback_data import choice_group_callback
from tgbot.keyboards.inline.choice_group_buttons import create_choice_groups_keyboard
from tgbot.loader import dp, db
from tgbot.states.choice_group import GroupChoice


@dp.message_handler(state=GroupChoice.getting_choice)
async def getting_choice_for_student(message: Message) -> None:
    groups_list = await db.get_groups_by_name(message.text)
    if len(groups_list) == 0:
        await GroupChoice.wrong_group.set()
        await groups_not_found_handler(message)
    elif len(groups_list) > 60:
        await GroupChoice.too_many_groups.set()
        await groups_are_too_many_handler(message)
    else:
        with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
            await message.chat.delete_message(message.message_id - 1)
            await message.delete()
        answer_msg = await message.answer("Выберите группу из списка:")
        await answer_msg.edit_reply_markup(
            reply_markup=await create_choice_groups_keyboard(groups_list)
        )
        await GroupChoice.choosing.set()


@dp.message_handler(state=GroupChoice.too_many_groups)
async def groups_are_too_many_handler(message: Message) -> None:
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.chat.delete_message(message.message_id - 1)
        await message.delete()
    await message.answer(
        f'Групп, содержащих в названии "<i>{message.text}</i>" слишком много!\n'
        "Попробуйте ввести подробнее:"
    )
    await GroupChoice.getting_choice.set()


@dp.message_handler(state=GroupChoice.wrong_group)
async def groups_not_found_handler(message: Message) -> None:
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.chat.delete_message(message.message_id - 1)
        await message.delete()
    await message.answer(
        f"Группа \"<i>{message.text.replace('>', '').replace('<', '')}</i>\" не найдена!\n"
        "Попробуйте ещё раз или воспользуйтесь навигацией с помощью команды /group:"
    )
    await GroupChoice.getting_choice.set()


@dp.callback_query_handler(choice_group_callback.filter(), state=GroupChoice.choosing)
async def group_viewing_schedule_handler(
        query: CallbackQuery, callback_data: dict, state: FSMContext
) -> None:
    await state.finish()
    await query.answer(cache_time=1)
    logging.info("call = %s", callback_data)
    await send_schedule(query.message, callback_data, state, subscription=True)
