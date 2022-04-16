import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputMedia, InputFile

from handlers.users.helpers import check_message_content_type
from keyboards.inline.callback_data import timetable_callback
from keyboards.inline.timetable_buttons import create_timetable_keyboard
from loader import dp
from utils.timetable.api import get_teacher_timetable_week, get_teacher_timetable_day, get_group_timetable_day, \
    get_group_timetable_week


async def timetable_keyboard_handler_helper(query: CallbackQuery, state_data: dict, text: str):
    is_picture = await check_message_content_type(query)
    if is_picture:
        answer_msg = await query.message.edit_media(media=InputMedia(
            media=InputFile("utils/image_converter/output.png")))
        await answer_msg.edit_caption(caption=text.split('\n')[1] + "\nТЕСТОВЫЙ РЕЖИМ!!!")
    else:
        answer_msg = await query.message.edit_text(text=text)

    day_counter = state_data.get("day_counter") if state_data.get("day_counter") else 0
    await answer_msg.edit_reply_markup(reply_markup=await create_timetable_keyboard(day_counter=day_counter,
                                                                                    is_picture=is_picture))


@dp.callback_query_handler(timetable_callback.filter(button=['1-1', '1-2', '1-3']))
async def timetable_days_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")

    async with state.proxy() as state_data:
        state_data["week_counter"] = None
        try:
            if state_data["day_counter"] is None:
                state_data["day_counter"] = 0
        except KeyError:
            state_data["day_counter"] = 0

        match callback_data["button"]:
            case '1-1':
                state_data["day_counter"] -= 1
            case '1-2':
                state_data["day_counter"] = 0
            case '1-3':
                state_data["day_counter"] += 1
    data = await state.get_data()

    if data["user_type"] == "teacher":
        text = await get_teacher_timetable_day(teacher_id=data["tt_id"], day_counter=data.get("day_counter"))
    else:
        text = await get_group_timetable_day(group_id=data["tt_id"], day_counter=data.get("day_counter"))
    await timetable_keyboard_handler_helper(query, await state.get_data(), text)


@dp.callback_query_handler(timetable_callback.filter(button=['2-1', '2-2']))
async def timetable_weeks_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=2)
    logging.info(f"call = {callback_data}")

    async with state.proxy() as state_data:
        state_data["day_counter"] = None
        try:
            if state_data["week_counter"] is None:
                state_data["week_counter"] = 0
        except KeyError:
            state_data["week_counter"] = 0

        match callback_data["button"]:
            case '2-1':
                state_data["week_counter"] = 0
            case '2-2':
                state_data["week_counter"] += 1
    data = await state.get_data()

    if data["user_type"] == "teacher":
        text = await get_teacher_timetable_week(teacher_id=data["tt_id"], week_counter=data.get("week_counter"))
    else:
        text = await get_group_timetable_week(group_id=data["tt_id"], week_counter=data.get("week_counter"))
    await timetable_keyboard_handler_helper(query, await state.get_data(), text)


@dp.callback_query_handler(timetable_callback.filter(button='3-1'))
async def timetable_type_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=5)
    logging.info(f"call = {callback_data}")

    is_picture = not await check_message_content_type(query)

    data = await state.get_data()
    if data["user_type"] == "teacher":
        if data.get("day_counter") is not None:
            text = await get_teacher_timetable_day(teacher_id=data["tt_id"], day_counter=data.get("day_counter"))
        elif data.get("week_counter") is not None:
            text = await get_teacher_timetable_week(teacher_id=data["tt_id"], week_counter=data.get("week_counter"))
        else:
            text = await get_teacher_timetable_week(teacher_id=data["tt_id"])
    else:
        if data.get("day_counter") is not None:
            text = await get_group_timetable_day(group_id=data["tt_id"], day_counter=data.get("day_counter"))
        elif data.get("week_counter") is not None:
            text = await get_group_timetable_week(group_id=data["tt_id"], week_counter=data.get("week_counter"))
        else:
            text = await get_group_timetable_week(group_id=data["tt_id"])

    if is_picture:
        answer_msg = await query.message.answer_photo(photo=InputFile("utils/image_converter/output.png"))
        await answer_msg.edit_caption(caption=text.split('\n')[1] + "\nТЕСТОВЫЙ РЕЖИМ!!!")
    else:
        answer_msg = await query.message.answer(text=text)
    await query.message.delete()
    await answer_msg.edit_reply_markup(reply_markup=await create_timetable_keyboard(is_picture=is_picture))
