import logging

from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, BotCommandScopeAllPrivateChats
from aiogram.utils.i18n import gettext as _

from tgbot.config import bot
from tgbot.keyboards.inline import create_start_choice_keyboard, create_settings_keyboard
from tgbot.misc.states import SearchEducator, SearchGroup
from tgbot.services.db_api.db_commands import database

router = Router()


async def set_commands(_bot: Bot):
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


@router.message(commands=["start"], state="*")
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    logging.info("start -- id:%s", message.from_user.id)
    await message.answer(
        text=_("👋🏻 <b>Добро пожаловать, {name}!</b>\n"
               "ℹ️ Следуйте указаниям для настройки\n"
               "❕ Для корректной работы взаимодействуйте только с последним сообщением бота\n"
               "➖➖➖➖➖➖➖➖➖➖➖➖\n"
               "⬇️ Получить расписание по:").format(name=message.from_user.full_name),
        reply_markup=await create_start_choice_keyboard(),
    )


@router.message(commands=["educator"], state="*")
async def educator_search_command(message: Message, state: FSMContext):
    await message.answer(_("🔎 Введите фамилию преподавателя для поиска:"))
    await state.set_state(SearchEducator.getting_choice)


@router.message(commands=["group"], state="*")
async def group_search_command(message: Message, state: FSMContext):
    await message.answer(_("🔎 Введите название группы для поиска:\n"
                           "*️⃣ <i>например, 20.Б08-мм</i>"))
    await state.set_state(SearchGroup.getting_choice)


@router.message(commands=["settings"], state="*")
async def settings_command(message: Message):
    user = await database.get_user(tg_user_id=message.chat.id)
    settings = await database.get_settings(user)

    text = _("📅 Основное расписание:\n — ")
    # Добавить получение расписания
    text += _("\n\n⚙️ Текущие настройки:")
    await message.answer(text=text, reply_markup=await create_settings_keyboard(settings))


@router.message(commands=["help"])
async def bot_help_command(message: Message):
    answer = _("🤖 Список команд: \n")
    commands = await bot.get_my_commands()
    for cmd in commands:
        answer += f"/{cmd.command} — {cmd.description}\n"
    await message.answer(answer)
