from aiogram.types import Message


async def change_message_to_progress(message: Message, is_picture: bool = False) -> None:
    if is_picture:
        await message.edit_caption("🕒 <i>Загрузка...</i>")
    else:
        await message.edit_text("⏳")
