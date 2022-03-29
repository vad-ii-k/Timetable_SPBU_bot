from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandSettings
from keyboards.inline.settings_buttons import create_settings_keyboard
from loader import dp


@dp.message_handler(CommandSettings(), state="*")
async def bot_settings(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(text="Настройки: ",
                         reply_markup=await create_settings_keyboard())
