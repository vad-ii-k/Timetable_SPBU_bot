""" Handling events that other handlers missed """

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

router = Router()


@router.message()
async def unexpected_message_handler(message: Message):
    """
    Deleting an unexpected message
    :param message:
    """
    await message.delete()


@router.callback_query()
async def unexpected_callback_handler(callback: CallbackQuery):
    """
    Sending a warning message in response to an unexpected callback
    :param callback:
    """
    await callback.message.answer(
        _(
            "⛔️️ Запрос не обработан!\n"
            "⚠️ Пожалуйста, не используйте старые сообщения для взаимодействия с ботом\n"
            "✳️ Вы можете получить своё расписание командой /my_schedule"
        )
    )
