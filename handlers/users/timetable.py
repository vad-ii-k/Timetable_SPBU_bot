import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputMedia, InputFile

from keyboards.inline.callback_data import timetable_callback
from keyboards.inline.timetable_buttons import create_timetable_keyboard
from loader import dp
from utils.tt_api import teacher_timetable_week, teacher_timetable_day, group_timetable_day, group_timetable_week


async def check_message_content_type(call: CallbackQuery) -> bool:
    is_picture = (call.message.content_type == 'photo')
    if is_picture:
        await call.message.edit_caption("<i>Получение расписания...</i>")
    else:
        await call.message.edit_text("<i>Получение расписания...</i>")
    return is_picture


async def timetable_keyboard_handler_helper(call: CallbackQuery, callback_data: dict, state_data: dict, text: str):
    is_picture = await check_message_content_type(call)
    if is_picture:
        media = InputMedia(media=InputFile("utils/image_converter/output.png"), caption=text.split('\n')[1])
        await call.message.edit_media(media=media)
    else:
        await call.message.edit_text(text=text)

    day_counter = state_data.get("day_counter") if state_data.get("day_counter") else 0
    await call.message.edit_reply_markup(reply_markup=await create_timetable_keyboard(user_type=callback_data["type"],
                                                                                      tt_id=callback_data["Id"],
                                                                                      day_counter=day_counter,
                                                                                      is_picture=is_picture))


@dp.callback_query_handler(timetable_callback.filter(button=['1-1', '1-2', '1-3']))
async def timetable_keyboard_handler_1_row(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=1)
    logging.info(f"call = {callback_data}")

    data = await state.get_data()
    if data.get("week_counter"):
        await state.reset_data()
    day_counter = data.get("day_counter")
    if day_counter is None:
        day_counter = 0

    if callback_data["button"] == '1-1':
        day_counter -= 1
    elif callback_data["button"] == '1-2':
        day_counter = 0
    elif callback_data["button"] == '1-3':
        day_counter += 1
    await state.update_data(day_counter=day_counter)
    data = await state.get_data()

    if data.get("week_counter"):
        data.pop("week_counter")

    if callback_data["type"] == "teacher":
        text = await teacher_timetable_day(teacher_id=callback_data["Id"], day_counter=data.get("day_counter"))
    else:
        text = await group_timetable_day(group_id=callback_data["Id"], day_counter=data.get("day_counter"))
    await timetable_keyboard_handler_helper(call, callback_data, await state.get_data(), text)


@dp.callback_query_handler(timetable_callback.filter(button=['2-1', '2-2']))
async def timetable_keyboard_handler_2_row(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=2)
    logging.info(f"call = {callback_data}")

    data = await state.get_data()
    if data.get("day_counter"):
        await state.reset_data()
    if data.get("week_counter") is None:
        await state.update_data(week_counter=0)
    data = await state.get_data()

    if callback_data["button"] == '2-1':
        await state.update_data(week_counter=0)
    elif callback_data["button"] == '2-2':
        await state.update_data(week_counter=data.get("week_counter") + 1)
    data = await state.get_data()

    if callback_data["type"] == "teacher":
        text = await teacher_timetable_week(teacher_id=callback_data["Id"], week_counter=data.get("week_counter"))
    else:
        text = await group_timetable_week(group_id=callback_data["Id"], week_counter=data.get("week_counter"))
    await timetable_keyboard_handler_helper(call, callback_data, await state.get_data(), text)


@dp.callback_query_handler(timetable_callback.filter(button='3-1'))
async def timetable_keyboard_handler_3(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=5)
    logging.info(f"call = {callback_data}")

    data = await state.get_data()
    if callback_data["type"] == "teacher":
        if data.get("day_counter"):
            text = await teacher_timetable_day(teacher_id=callback_data["Id"], day_counter=data.get("day_counter"))
        elif data.get("week_counter"):
            text = await teacher_timetable_week(teacher_id=callback_data["Id"], week_counter=data.get("week_counter"))
        else:
            text = await teacher_timetable_week(teacher_id=callback_data["Id"])
    else:
        if data.get("day_counter"):
            text = await group_timetable_day(group_id=callback_data["Id"], day_counter=data.get("day_counter"))
        elif data.get("week_counter"):
            text = await group_timetable_week(group_id=callback_data["Id"], week_counter=data.get("week_counter"))
        else:
            text = await group_timetable_week(group_id=callback_data["Id"])

    is_picture = not await check_message_content_type(call)
    if is_picture:
        media = InputFile("utils/image_converter/output.png")
        answer = await call.message.answer_photo(photo=media, caption=text.split('\n')[1])
    else:
        answer = await call.message.answer(text=text)
    await call.message.delete()
    await answer.edit_reply_markup(reply_markup=await create_timetable_keyboard(user_type=callback_data["type"],
                                                                                tt_id=callback_data["Id"],
                                                                                is_picture=is_picture))
