from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import html

from tgbot.keyboards.inline import create_educators_keyboard
from tgbot.misc.states import SearchEducator
from tgbot.services.timetable_api.timetable_api import educator_search

router = Router()


@router.message(SearchEducator.getting_choice)
async def getting_choice_for_educator(message: Message, state: FSMContext):
    answer_msg = await message.answer("⏳")
    teachers_list = await educator_search(message.text)
    if len(teachers_list) == 0:
        await state.set_state(SearchEducator.wrong_last_name)
        await wrong_last_name(message, state)
    elif len(teachers_list) > 50:
        await state.set_state(SearchEducator.widespread_last_name)
        await widespread_last_name(message, state)
    else:
        await answer_msg.edit_text(
            text="⬇️ Выберите преподавателя из списка:",
            reply_markup=await create_educators_keyboard(teachers_list)
        )
        await state.set_state(SearchEducator.choosing)


@router.message(SearchEducator.choosing)
async def choosing_teacher(message: Message):
    await message.delete()


@router.message(SearchEducator.wrong_last_name)
async def wrong_last_name(message: Message, state: FSMContext):
    await message.delete()
    await message.answer(
        f"❌ Преподаватель \"<i>{html.quote(message.text)}</i>\" не найден!\n"
        "Пожалуйста, введите другую фамилию:"
    )
    await state.set_state(SearchEducator.getting_choice)


@router.message(SearchEducator.widespread_last_name)
async def widespread_last_name(message: Message, state: FSMContext):
    await message.delete()
    await message.answer(
        f'❌ Фамилия "<i>{message.text}</i>" очень распространена\n'
        "Попробуйте ввести фамилию и первую букву имени:"
    )
    await state.set_state(SearchEducator.getting_choice)
