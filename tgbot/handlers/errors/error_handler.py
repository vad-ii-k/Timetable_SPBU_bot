import logging

from aiogram.types import Update
from aiogram.utils.exceptions import TelegramAPIError, MessageNotModified, CantParseEntities, \
    MessageToDeleteNotFound

from tgbot.loader import dp


@dp.errors_handler()
async def errors_handler(update: Update, exception: Exception):
    """
    Error's handler.

    :param update: Update
    :param exception: Exception
    :return:
    """
    if isinstance(exception, MessageNotModified):
        logging.exception("Message is not modified")
        return True

    if isinstance(exception, CantParseEntities):
        logging.exception(f"CantParseEntities: {exception} \nUpdate: {update}")
        await update.callback_query.message.answer(
            text="🆘 Расписание не может быть отображено в текстовом виде,\n"
                 "   из-за особенностей сайта timetable.spbu.ru\n"
                 "⚙️ Измените вид расписания по умолчанию в /setting"
        )
        return True

    if isinstance(exception, TelegramAPIError):
        logging.exception(f"TelegramAPIError: {exception} \nUpdate: {update}")
        return True

    if isinstance(exception, MessageToDeleteNotFound):
        logging.exception(f"MessageToDeleteNotFound: {exception} \nUpdate: {update}")
        return True

    logging.exception(f"Update: {update} \n{exception}")
