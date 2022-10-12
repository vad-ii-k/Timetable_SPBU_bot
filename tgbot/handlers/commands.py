import logging

from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, BotCommandScopeAllPrivateChats
from aiogram.utils.i18n import gettext as _
from aiogram.filters import Command

from tgbot.config import bot
from tgbot.handlers.helpers import send_schedule
from tgbot.keyboards.inline import create_start_choice_keyboard, create_settings_keyboard
from tgbot.misc.states import Searching, UserType
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


@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    logging.info("start -- id:%s", message.from_user.id)
    await message.answer(
        text=_("👋🏻 <b>Добро пожаловать, {name}!</b>\n"
               "ℹ️ Следуйте указаниям для настройки\n"
               "❕ Для корректной работы взаимодействуйте только с последним сообщением бота\n"
               "➖➖➖➖➖➖➖➖➖➖➖➖\n"
               "⬇️ Получить расписание по:".format(name=message.from_user.full_name)),
        reply_markup=await create_start_choice_keyboard(),
    )


@router.message(Command("educator"))
async def educator_search_command(message: Message, state: FSMContext):
    await message.answer(_("🔎 Введите фамилию преподавателя для поиска:"))
    await state.set_state(Searching.getting_educator_choice)


@router.message(Command("group"))
async def group_search_command(message: Message, state: FSMContext):
    await message.answer(_("🔎 Введите название группы для поиска:\n"
                           "*️⃣ <i>например, 20.Б08-мм</i>"))
    await state.set_state(Searching.getting_group_choice)


@router.message(Command("settings"))
async def settings_command(message: Message):
    user = await database.get_user(tg_user_id=message.chat.id)
    settings = await database.get_settings(user)
    main_schedule = await database.get_main_schedule(user_id=user.user_id)

    text = _("📅 <b>Основное расписание:</b>\nㅤㅤ")
    if main_schedule:
        text += f"{'👨‍👩‍👧‍👦' if main_schedule.user_type_is_student else '👨🏼‍🏫'} {main_schedule.name}"
    else:
        text += _("🚫 Не выбрано")
    text += _("\n\n⚙️ <b>Текущие настройки:</b>")
    await message.answer(text=text, reply_markup=await create_settings_keyboard(settings))


@router.message(Command("my_schedule"), flags={'chat_action': 'typing'})
async def my_schedule_command(message: Message, state: FSMContext):
    user = await database.get_user(tg_user_id=message.chat.id)
    main_schedule = await database.get_main_schedule(user_id=user.user_id)
    if main_schedule:
        user_type = UserType.STUDENT if main_schedule.user_type_is_student else UserType.EDUCATOR
        await state.update_data({'tt_id': main_schedule.timetable_id, 'user_type': user_type})
        await send_schedule(state, subscription=False, tg_user_id=message.from_user.id)
    else:
        await message.answer(text=_("🚫 Основное расписание отсутствует\n"
                                    "1. 🔎 Воспользуйтесь одной из команд:\n"
                                    "      /start, /group или /educator\n"
                                    "2. 🔖 Выберите нужное Вам расписание\n"
                                    "3. ✅ Сделайте расписание основным"))
        await message.delete()


@router.message(Command("help"))
async def help_command(message: Message):
    answer = _("🤖 Список команд: \n")
    commands = await bot.get_my_commands()
    for cmd in commands:
        answer += f"/{cmd.command} — {cmd.description}\n"
    await message.answer(answer)
