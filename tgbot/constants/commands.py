from aiogram.types import BotCommand

bot_commands: [BotCommand] = [
    BotCommand(command="start", description="🔄 Перезапустить бота"),
    BotCommand(command="my_schedule", description="📆 Получить своё расписание"),
    BotCommand(command="settings", description="⚙️ Настройки"),
    BotCommand(command="help", description="📒 Вывести справку о командах"),
    BotCommand(command="educator", description="🧑‍🏫️ Посмотреть расписание преподавателя"),
    BotCommand(command="group", description="👨‍👩‍👧‍👦 Посмотреть расписание группы"),
]
