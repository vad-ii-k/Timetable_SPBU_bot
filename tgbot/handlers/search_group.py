from aiogram import Router
from aiogram import html
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from tgbot.cb_data import TTObjectChoiceCallbackFactory
from tgbot.handlers.helpers import send_schedule
from tgbot.keyboards.inline import create_groups_keyboard
from tgbot.misc.states import SearchGroup

router = Router()


@router.message(SearchGroup.getting_choice)
async def getting_choice_for_student(message: Message, state: FSMContext):
    loading_msg = await message.answer("⏳")
    groups_list = []
    # groups_list = await db.get_groups_by_name(message.text)
    if len(groups_list) == 0:
        await groups_not_found(answer_msg=loading_msg, received_msg_text=message.text)
    elif len(groups_list) > 50:
        await groups_are_too_many(answer_msg=loading_msg, received_msg_text=message.text)
    else:
        await loading_msg.edit_text(
            text="⬇️ Выберите группу из списка:",
            reply_markup=await create_groups_keyboard(groups_list)
        )
        await state.set_state(SearchGroup.choosing)


@router.message(SearchGroup.choosing)
async def choosing_teacher(message: Message):
    await message.delete()


async def groups_not_found(answer_msg: Message, received_msg_text: str):
    await answer_msg.edit_text(
        "Группа \"<i>{group_name}</i>\" не найдена!\n"
        "Попробуйте ещё раз или воспользуйтесь навигацией с помощью команды /group:".format(
            group_name=html.quote(received_msg_text)
        )
    )


async def groups_are_too_many(answer_msg: Message, received_msg_text: str):
    await answer_msg.edit_text(
        "Групп, содержащих в названии \"<i>{group_name}</i>\" слишком много!\n"
        "Попробуйте ввести подробнее:".format(group_name=received_msg_text)
    )


@router.callback_query(
    TTObjectChoiceCallbackFactory.filter(F.user_type.STUDENT), SearchGroup.choosing, flags={'chat_action': 'typing'}
)
async def group_viewing_schedule_handler(
        callback: CallbackQuery, callback_data: TTObjectChoiceCallbackFactory, state: FSMContext
) -> None:
    await state.set_state(state=None)
    await send_schedule(callback.message, callback_data, subscription=True)
    await callback.answer(cache_time=1)
