""" Handling the start menu button click """

from aiogram import F, Router, flags
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from tgbot.handlers.helpers import change_message_to_loading
from tgbot.keyboards.inline import create_study_divisions_keyboard
from tgbot.misc.cb_data import StartMenuCallbackFactory
from tgbot.misc.states import Searching
from tgbot.services.timetable_api.timetable_api import get_study_divisions

router = Router()


@router.callback_query(StartMenuCallbackFactory.filter(F.type == "student_search"))
async def group_search_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handling clicking on the group search button by name
    :param callback:
    :param state:
    """
    await callback.message.edit_text(_("👨‍👩‍👧‍👦 Введите название группы:\n *️⃣ <i>например, 20.Б08-мм</i>"))
    await state.set_state(Searching.getting_group_choice)


@router.callback_query(StartMenuCallbackFactory.filter(F.type == "student_navigation"))
@flags.chat_action(ChatAction.TYPING)
async def student_navigation_callback(callback: CallbackQuery):
    """
    Handling clicking on the group search button by program navigation
    :param callback:
    """
    await change_message_to_loading(callback.message)
    study_divisions = await get_study_divisions()
    await callback.message.delete()
    await callback.message.answer(
        text=_("⬇️ Выберите направление: "),
        reply_markup=await create_study_divisions_keyboard(study_divisions),
    )
    await callback.answer(cache_time=2)


@router.callback_query(StartMenuCallbackFactory.filter(F.type == "educator_search"))
async def educator_search_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handling clicking on the teacher search button by last name
    :param callback:
    :param state:
    """
    await callback.message.edit_text(_("🧑‍🏫 Введите фамилию преподавателя:"))
    await state.set_state(Searching.getting_educator_choice)
