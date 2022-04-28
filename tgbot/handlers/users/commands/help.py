from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp
from tgbot.loader import dp, bot


@dp.message_handler(CommandHelp(), state="*")
async def bot_help(message: types.Message):
    answer = "🤖 Список команд: \n"
    commands = await bot.get_my_commands()
    for item in commands:
        answer += '/' + item["command"] + ' — ' + item["description"] + '\n'
    await message.answer(answer)
