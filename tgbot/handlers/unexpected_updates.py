from aiogram import Router
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message()
async def unexpected_message_handler(message: Message):
    await message.delete()


@router.callback_query()
async def unexpected_callback_handler(callback: CallbackQuery):
    await callback.message.delete()
