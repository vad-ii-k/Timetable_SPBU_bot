from aiogram import types


async def set_default_commands(dp) -> None:
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "🔄 Перезапустить бота"),
            types.BotCommand("my_schedule", "📆 Получить своё расписание"),
            types.BotCommand("settings", "⚙️ Настройки"),
            types.BotCommand("help", "📒 Вывести справку"),
            types.BotCommand("educator", "🧑‍🏫️ Посмотреть расписание преподавателя"),
            types.BotCommand("group", "👨‍👩‍👧‍👦 Посмотреть расписание группы")
        ]
    )
