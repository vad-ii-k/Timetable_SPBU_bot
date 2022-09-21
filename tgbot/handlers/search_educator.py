from aiogram import Router
from aiogram import html
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _
from magic_filter import F

from tgbot.cb_data import TTObjectChoiceCallbackFactory
from tgbot.handlers.helpers import send_schedule
from tgbot.keyboards.inline import create_educators_keyboard
from tgbot.misc.states import SearchEducator
from tgbot.services.timetable_api.timetable_api import educator_search

router = Router()


@router.message(SearchEducator.getting_choice, flags={'chat_action': 'typing'})
async def getting_choice_for_educator(message: Message, state: FSMContext):
    teachers_list = await educator_search(message.text)
    if len(teachers_list) == 0:
        await message.answer(_("❌ Преподаватель \"<i>{last_name}</i>\" не найден!\n"
                               "Пожалуйста, введите другую фамилию:").format(last_name=html.quote(message.text)))
    elif len(teachers_list) > 50:
        await message.answer(_("❌ Фамилия \"<i>{last_name}</i>\" очень распространена\n"
                               "Попробуйте ввести фамилию и первую букву имени:").format(last_name=message.text))
    else:
        await message.answer(text=_("⬇️ Выберите преподавателя из списка:"),
                             reply_markup=await create_educators_keyboard(teachers_list))
        await state.set_state(SearchEducator.choosing)


@router.message(SearchEducator.choosing)
async def choosing_teacher(message: Message):
    await message.delete()


@router.callback_query(
    TTObjectChoiceCallbackFactory.filter(F.user_type.EDUCATOR), SearchEducator.choosing, flags={'chat_action': 'typing'}
)
async def teacher_viewing_schedule_handler(
        callback: CallbackQuery, callback_data: TTObjectChoiceCallbackFactory, state: FSMContext
) -> None:
    await state.set_state(state=None)
    await send_schedule(callback.message, callback_data, subscription=True)
    await callback.answer(cache_time=1)
