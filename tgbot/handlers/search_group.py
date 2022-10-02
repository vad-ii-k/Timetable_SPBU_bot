from aiogram import Router
from aiogram import html
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _
from magic_filter import F

from tgbot.cb_data import TTObjectChoiceCallbackFactory
from tgbot.handlers.helpers import send_schedule
from tgbot.keyboards.inline import create_groups_keyboard
from tgbot.misc.states import SearchGroup
from tgbot.services.db_api.db_commands import database

router = Router()


@router.message(SearchGroup.getting_choice)
async def getting_choice_for_student(message: Message, state: FSMContext):
    groups_list = await database.get_groups_by_name(message.text)
    if len(groups_list) == 0:
        await message.answer(_("Группа \"<i>{group_name}</i>\" не найдена!\n"
                               "Попробуйте ещё раз или воспользуйтесь навигацией с помощью команды /start:").
                             format(group_name=html.quote(message.text)))
    elif len(groups_list) > 50:
        await message.answer(_("Групп, содержащих в названии \"<i>{group_name}</i>\" слишком много!\n"
                               "Попробуйте ввести подробнее:").format(group_name=message.text))
    else:
        await message.answer(
            text=_("⬇️ Выберите группу из списка:"),
            reply_markup=await create_groups_keyboard(groups_list)
        )
        await state.set_state(SearchGroup.choosing)


@router.message(SearchGroup.choosing)
async def choosing_group(message: Message):
    await message.delete()


@router.callback_query(
    TTObjectChoiceCallbackFactory.filter(F.user_type.STUDENT), SearchGroup.choosing, flags={'chat_action': 'typing'}
)
async def group_viewing_schedule_handler(
        callback: CallbackQuery, callback_data: TTObjectChoiceCallbackFactory, state: FSMContext
) -> None:
    await state.set_state(state=None)
    await send_schedule(callback, callback_data, subscription=True)
    await callback.answer(cache_time=1)
