from aiogram import Router
from aiogram import html
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.cb_data import EducatorChoiceCallbackFactory
from tgbot.keyboards.inline import create_educators_keyboard
from tgbot.misc.states import SearchEducator
from tgbot.services.timetable_api.timetable_api import educator_search

router = Router()


@router.message(SearchEducator.getting_choice)
async def getting_choice_for_educator(message: Message, state: FSMContext):
    loading_msg = await message.answer("⏳")
    teachers_list = await educator_search(message.text)
    if len(teachers_list) == 0:
        await wrong_last_name(answer_msg=loading_msg, received_msg_text=message.text)
    elif len(teachers_list) > 50:
        await widespread_last_name(answer_msg=loading_msg, received_msg_text=message.text)
    else:
        await loading_msg.edit_text(
            text="⬇️ Выберите преподавателя из списка:",
            reply_markup=await create_educators_keyboard(teachers_list)
        )
        await state.set_state(SearchEducator.choosing)


@router.message(SearchEducator.choosing)
async def choosing_teacher(message: Message):
    await message.delete()


async def wrong_last_name(answer_msg: Message, received_msg_text: str):
    await answer_msg.edit_text(
        "❌ Преподаватель \"<i>{last_name}</i>\" не найден!\n"
        "Пожалуйста, введите другую фамилию:".format(last_name=html.quote(received_msg_text))
    )


async def widespread_last_name(answer_msg: Message, received_msg_text: str):
    await answer_msg.edit_text(
        '❌ Фамилия "<i>{last_name}</i>" очень распространена\n'
        "Попробуйте ввести фамилию и первую букву имени:".format(last_name=received_msg_text)
    )


@router.callback_query(EducatorChoiceCallbackFactory.filter(), SearchEducator.choosing)
async def teacher_viewing_schedule_handler(
        callback: CallbackQuery, callback_data: EducatorChoiceCallbackFactory, state: FSMContext
) -> None:
    await state.set_state(state=None)
    # await send_schedule(callback.message, callback_data, state, subscription=True)
    await callback.answer(cache_time=1)
