import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandSettings
from aiogram.types import CallbackQuery

from keyboards.inline.callback_data import settings_callback
from keyboards.inline.settings_buttons import create_settings_keyboard
from loader import dp, db
from utils.db_api.database import Settings


@dp.message_handler(CommandSettings(), state="*")
async def bot_settings(message: types.Message, state: FSMContext):
    await state.finish()
    settings = await db.get_settings(tg_user_id=message.from_user.id)
    await message.answer(text="Текущие настройки: ",
                         reply_markup=await create_settings_keyboard(settings))


@dp.callback_query_handler(settings_callback.filter(type='schedule_view'))
async def settings_keyboard_handler_3(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=1)
    logging.info(f"call = {callback_data}")
    settings = await db.get_settings(tg_user_id=call.from_user.id)
    await settings.update(schedule_view_is_picture=not settings.schedule_view_is_picture).apply()

    await call.message.edit_text(text="Вид расписания по умолчанию успешно изменён!\n\nТекущие настройки:")
    await call.message.edit_reply_markup(reply_markup=await create_settings_keyboard(settings))
