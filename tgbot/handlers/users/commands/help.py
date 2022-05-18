from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from tgbot.loader import dp, bot


@dp.message_handler(CommandHelp(), state="*")
async def bot_help_command(message: types.Message) -> None:
    """
    Handler for command: help.

    :param message: message from user
    :return:
    """
    answer = "🤖 Список команд: \n"
    commands = await bot.get_my_commands()
    for cmd in commands:
        answer += f"/{cmd['command']} — {cmd['description']}\n"
    await message.answer(answer)
