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
    settings = await db.get_settings(tg_user_id=message.from_user.id)
    await message.answer(text="Текущие настройки: ",
                         reply_markup=await create_settings_keyboard(settings))


@dp.callback_query_handler(settings_callback.filter(type='schedule_view'))
async def settings_keyboard_handler_3(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=1)
    logging.info(f"call = {callback_data}")
    settings = await db.get_settings(tg_user_id=query.from_user.id)
    await settings.update(schedule_view_is_picture=not settings.schedule_view_is_picture).apply()

    await query.message.edit_text(text="Вид расписания по умолчанию успешно изменён!\n\nТекущие настройки:")
    await query.message.edit_reply_markup(reply_markup=await create_settings_keyboard(settings))


@dp.callback_query_handler(schedule_subscription_callback.filter())
async def schedule_subscription_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    logging.info(f"call = {callback_data}")
    data = await state.get_data()
    # TODO
    if callback_data["answer"] == '1':
        text = "Вы подписались!"
    else:
        text = "Вы отказались от подписки!"
    await query.answer(text=text, show_alert=False, cache_time=3)

    await query.message.delete()
