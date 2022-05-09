from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp
from tgbot.loader import dp, bot


@dp.message_handler(CommandHelp(), state="*")
async def bot_help(message: types.Message) -> None:
    answer = "🤖 Список команд: \n"
    commands = await bot.get_my_commands()
    for cmd in commands:
        answer += '/' + cmd["command"] + ' — ' + cmd["description"] + '\n'
    await message.answer(answer)
