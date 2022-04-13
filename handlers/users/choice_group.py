import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputFile

from keyboards.inline.callback_data import choice_group_callback
from keyboards.inline.choice_group_buttons import create_choice_groups_keyboard
from keyboards.inline.schedule_subscription_buttons import create_schedule_subscription_keyboard
from keyboards.inline.timetable_buttons import create_timetable_keyboard
from loader import dp, db
from states.choice_group import GroupChoice
from utils.tt_api import group_timetable_week


@dp.message_handler(state=GroupChoice.getting_choice)
async def getting_choice_for_student(message: types.Message):
    answer = await message.answer("<i>Получение списка групп...</i>")
    groups_list = await db.get_groups_by_name(message.text)
    if len(groups_list) > 0:
        await answer.edit_text("Выберите группу из списка:")
        await answer.edit_reply_markup(reply_markup=await create_choice_groups_keyboard(groups_list))
        await GroupChoice.choosing.set()
    else:
        await answer.edit_text("Ошибка...")


@dp.callback_query_handler(choice_group_callback.filter(), state=GroupChoice.choosing)
async def groups_keyboard_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")

    settings = await db.set_settings()
    is_picture = settings.schedule_view_is_picture
    await query.message.edit_text("<i>Получение расписания...</i>")
    text = await group_timetable_week(callback_data["group_id"])
    if is_picture:
        answer = await query.message.answer_photo(photo=InputFile("utils/image_converter/output.png"))
        await query.message.delete()
    else:
        answer = await query.message.edit_text(text)
    await state.update_data(user_type="student", tt_id=callback_data["group_id"],
                            group_name=text.split('\n', 1)[0])
    await answer.edit_reply_markup(reply_markup=await create_timetable_keyboard(is_picture=is_picture))

    await answer.answer(text="⚙️ Хотите сделать это расписание своим основным?",
                        reply_markup=await create_schedule_subscription_keyboard())
