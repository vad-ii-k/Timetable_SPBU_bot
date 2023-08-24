""" Handling the selection of a group or teacher from the suggested list """
from aiogram import Router, flags, html
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from tgbot.handlers.helpers import send_schedule
from tgbot.keyboards.inline import create_educators_keyboard, create_groups_keyboard
from tgbot.misc.cb_data import TTObjectChoiceCallbackFactory
from tgbot.misc.states import Searching
from tgbot.services.db_api.db_commands import database
from tgbot.services.timetable_api.timetable_api import educator_search

router = Router()


@router.message(Searching.getting_educator_choice)
@flags.chat_action(ChatAction.TYPING)
async def getting_choice_for_educator(message: Message, state: FSMContext):
    """
    Handling the selection of a teacher from the suggested list
    :param message:
    :param state:
    """
    teachers_list = await educator_search(message.text)
    if len(teachers_list) == 0:
        await message.answer(
            _(
                '❌ Преподаватель "<i>{last_name}</i>" не найден!\n'
                "Пожалуйста, введите другую фамилию:".format(last_name=html.quote(message.text))
            )
        )
    elif len(teachers_list) > 50:
        await message.answer(
            _(
                '❌ Фамилия "<i>{last_name}</i>" очень распространена\n'
                "Попробуйте ввести фамилию и первую букву имени:".format(last_name=message.text)
            )
        )
    else:
        await message.answer(
            text=_("⬇️ Выберите преподавателя из списка:"),
            reply_markup=await create_educators_keyboard(teachers_list),
        )
        await state.set_state(Searching.choosing)


@router.message(Searching.getting_group_choice)
async def getting_choice_for_student(message: Message, state: FSMContext):
    """
    Handling the selection of a group from the suggested list
    :param message:
    :param state:
    """
    groups_list = await database.get_groups_by_name(message.text)
    if len(groups_list) == 0:
        await message.answer(
            _(
                'Группа "<i>{group_name}</i>" не найдена!\n'
                "Попробуйте ещё раз или воспользуйтесь навигацией с помощью команды /start:".format(
                    group_name=html.quote(message.text)
                )
            )
        )
    elif len(groups_list) > 50:
        await message.answer(
            _(
                'Групп, содержащих в названии "<i>{group_name}</i>" слишком много!\n'
                "Попробуйте ввести подробнее:".format(group_name=message.text)
            )
        )
    else:
        await message.answer(
            text=_("⬇️ Выберите группу из списка:"),
            reply_markup=await create_groups_keyboard(groups_list),
        )
        await state.set_state(Searching.choosing)


@router.callback_query(TTObjectChoiceCallbackFactory.filter(), Searching.choosing)
@flags.chat_action(ChatAction.TYPING)
async def sending_schedule_after_search(
    callback: CallbackQuery, callback_data: TTObjectChoiceCallbackFactory, state: FSMContext
):
    """
    Sending a schedule for the selected group or teacher after selecting from the suggested list
    :param callback:
    :param callback_data:
    :param state:
    """
    await callback.message.delete()
    await state.set_state(state=None)
    await state.update_data({"tt_id": callback_data.tt_id, "user_type": callback_data.user_type})
    await send_schedule(state, subscription=True, tg_user_id=callback.from_user.id)
