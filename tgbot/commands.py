from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def set_commands(bot: Bot):
    data = [
        (
            [
                BotCommand(command="start", description="🔄 Перезапустить бота"),
                BotCommand(command="my_schedule", description="📆 Получить своё расписание"),
                BotCommand(command="settings", description="⚙️ Настройки"),
                BotCommand(command="help", description="📒 Вывести справку о командах"),
                BotCommand(command="educator", description="🧑‍🏫️ Посмотреть расписание преподавателя"),
                BotCommand(command="group", description="👨‍👩‍👧‍👦 Посмотреть расписание группы"),
            ],
            BotCommandScopeAllPrivateChats(),
            None
        )
    ]
    for commands_list, commands_scope, language in data:
        await bot.set_my_commands(commands=commands_list, scope=commands_scope, language_code=language)
