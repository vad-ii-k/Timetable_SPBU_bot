import logging
from aiogram.utils.exceptions import TelegramAPIError, MessageNotModified, CantParseEntities, MessageToDeleteNotFound
from tgbot.loader import dp


@dp.errors_handler()
async def errors_handler(update, exception):

    if isinstance(exception, MessageNotModified):
        logging.exception('Message is not modified')
        return True
      
    if isinstance(exception, CantParseEntities):
        logging.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, TelegramAPIError):
        logging.exception(f'TelegramAPIError: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, MessageToDeleteNotFound):
        logging.exception(f'MessageToDeleteNotFound: {exception} \nUpdate: {update}')
        return True

    logging.exception(f'Update: {update} \n{exception}')
