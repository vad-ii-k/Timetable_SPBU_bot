import datetime
import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from tgbot.handlers.users.commands.settings import bot_settings
from tgbot.keyboards.inline.callback_data import settings_callback, schedule_subscription_callback, \
    settings_daily_summary_callback
from tgbot.keyboards.inline.settings_buttons import create_settings_keyboard
from tgbot.keyboards.inline.settings_daily_summary_buttons import create_daily_summary_keyboard
from tgbot.loader import dp, db


@dp.callback_query_handler(settings_callback.filter(type='daily_summary'))
async def settings_keyboard_handler_1(query: CallbackQuery, callback_data: dict) -> None:
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")
    settings = await db.set_settings()
    await query.message.edit_text('⚙️<b> Выберите время для получения\nсводки расписания на день</b>\n'
                                  'Заранее вечером в ┃ В день занятий в')
    await query.message.edit_reply_markup(reply_markup=await create_daily_summary_keyboard(settings.daily_summary))


@dp.callback_query_handler(settings_daily_summary_callback.filter())
async def settings_keyboard_handler_1(query: CallbackQuery, callback_data: dict) -> None:
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")
    settings = await db.set_settings()
    if callback_data['choice'] != 'back':
        value = datetime.time(int(callback_data['choice'])) if callback_data['choice'] != 'disabling' else None
        await settings.update(daily_summary=value).apply()
    await query.message.delete()
    await bot_settings(query.message)


@dp.callback_query_handler(settings_callback.filter(type='schedule_view'))
async def settings_keyboard_handler_3(query: CallbackQuery, callback_data: dict) -> None:
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")
    settings = await db.set_settings()
    await settings.update(schedule_view_is_picture=not settings.schedule_view_is_picture).apply()
    await query.message.edit_reply_markup(reply_markup=await create_settings_keyboard(settings))


@dp.callback_query_handler(schedule_subscription_callback.filter())
async def schedule_subscription_handler(query: CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    logging.info(f"call = {callback_data}")

    if callback_data["answer"] == '1':
        data = await state.get_data()
        if data["user_type"] == 'teacher':
            await db.set_teacher_user(tt_id=int(data["tt_id"]))
        else:
            await db.set_student(tt_id=int(data["tt_id"]))
        text = "Вы подписались на расписание! ✅"
    else:
        text = "Вы отказались от подписки! ❌"
    await query.answer(text=text, show_alert=False)
    await query.message.delete()
