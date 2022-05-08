from aiogram.types import Message, ContentType

from tgbot.loader import dp


@dp.message_handler(content_types=[ContentType.ANY])
async def unexpected_message_handler(message: Message):
    await message.delete()
