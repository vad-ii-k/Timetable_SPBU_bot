import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandSettings
from aiogram.types import CallbackQuery

from keyboards.inline.callback_data import settings_callback, schedule_subscription_callback
from keyboards.inline.settings_buttons import create_settings_keyboard
from loader import dp, db


@dp.message_handler(CommandSettings(), state="*")
async def bot_settings(message: types.Message, state: FSMContext):
    await state.finish()
    user_db = await db.get_user()
    settings = await db.get_settings(user_db)

    text = "📅 Основное расписание:\n — "
    student = await db.get_student(user_db)
    if student:
        group = await db.get_group(student.group_id)
        text += '👨‍👩‍👧‍👦 ' + group.name
    else:
        teacher = await db.get_teacher(user_db)
        if teacher:
            text += '🧑‍🏫 ' + teacher.full_name
        else:
            text += "🚫 Отстутствует"

    text += "\n\n⚙️ Текущие настройки:"
    await message.answer(text=text, reply_markup=await create_settings_keyboard(settings))


@dp.callback_query_handler(settings_callback.filter(type='schedule_view'))
async def settings_keyboard_handler_3(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")
    settings = await db.set_settings()
    await settings.update(schedule_view_is_picture=not settings.schedule_view_is_picture).apply()

    text = "🆗 Вид расписания по умолчанию успешно изменён!\n\n⚙️ Текущие настройки:"
    await query.message.edit_text(text=text)
    await query.message.edit_reply_markup(reply_markup=await create_settings_keyboard(settings))


@dp.callback_query_handler(schedule_subscription_callback.filter())
async def schedule_subscription_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    logging.info(f"call = {callback_data}")

    if callback_data["answer"] == '1':
        data = await state.get_data()
        if data["user_type"] == 'teacher':
            teacher = await db.set_teacher(tt_id=int(data["tt_id"]), full_name=data["full_name"])
        else:
            student = await db.set_student(tt_id=int(data["tt_id"]))
        text = "Вы подписались на расписание! ✅"
    else:
        text = "Вы отказались от подписки! ❌"
    await query.answer(text=text, show_alert=False, cache_time=3)
    await query.message.delete()
