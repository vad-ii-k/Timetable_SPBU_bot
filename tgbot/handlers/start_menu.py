from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from magic_filter import F

from tgbot.cb_data import StartMenuCallbackFactory
from tgbot.handlers.helpers import change_message_to_progress
from tgbot.keyboards.inline import create_study_divisions_keyboard
from tgbot.misc.states import SearchEducator, SearchGroup
from tgbot.services.timetable_api.timetable_api import get_study_divisions

router = Router()


@router.callback_query(StartMenuCallbackFactory.filter(F.type == "student_search"))
async def group_search_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("👨‍👩‍👧‍👦 Введите название группы:\n *️⃣ <i>например, 20.Б08-мм</i>")
    await state.set_state(SearchGroup.getting_choice)


@router.callback_query(StartMenuCallbackFactory.filter(F.type == "student_navigation"))
async def student_navigation_callback(callback: CallbackQuery):
    await change_message_to_progress(callback.message)
    study_divisions = await get_study_divisions()
    await callback.message.edit_text(
        text=f"⬇️ Выберите направление: ",
        reply_markup=await create_study_divisions_keyboard(study_divisions)
    )
    await callback.answer(cache_time=2)


@router.callback_query(StartMenuCallbackFactory.filter(F.type == "educator_search"))
async def educator_search_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🧑‍🏫 Введите фамилию преподавателя:")
    await state.set_state(SearchEducator.getting_choice)
