"""
Setting and processing commands of a regular user
with the [Command](https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/command.html) filter
"""
import logging

from aiogram import Router, Bot, flags
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommandScopeAllPrivateChats
from aiogram.utils.i18n import gettext as _

from tgbot.constants.commands import bot_commands
from tgbot.handlers.helpers import send_schedule
from tgbot.keyboards.inline import create_start_menu_keyboard, create_settings_keyboard
from tgbot.misc.states import Searching
from tgbot.services.db_api.db_commands import database
from tgbot.services.schedule.data_classes import UserType

router = Router()


async def set_commands(bot_: Bot):
    """
    Setting the commands to be displayed in the menu
    :param bot_: telegram bot
    """
    data = [
        (
            bot_commands,
            BotCommandScopeAllPrivateChats(),
            None
        )
    ]
    for commands_list, commands_scope, language in data:
        await bot_.set_my_commands(commands=commands_list, scope=commands_scope, language_code=language)


@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    """
    Handling `start` command
    :param message: */start*
    :param state:
    """
    await state.clear()
    logging.info("start -- id:%s", message.from_user.id)
    await message.answer(
        text=(_("👋🏻 <b>Добро пожаловать, ")
              + f"{message.from_user.full_name}!</b>\n"
              + _("ℹ️ Следуйте указаниям для настройки\n"
                  "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                  "⬇️ Получить расписание по:")
              ),
        reply_markup=await create_start_menu_keyboard(),
    )


@router.message(Command("educator"))
async def educator_search_command(message: Message, state: FSMContext):
    """
    Handling `educator` command
    :param message: */educator*
    :param state:
    """
    await message.answer(_("🔎 Введите фамилию преподавателя для поиска:"))
    await state.set_state(Searching.getting_educator_choice)


@router.message(Command("group"))
async def group_search_command(message: Message, state: FSMContext):
    """
    Handling `group` command
    :param message: */group*
    :param state:
    """
    await message.answer(_("🔎 Введите название группы для поиска:\n"
                           "*️⃣ <i>например, 20.Б08-мм</i>"))
    await state.set_state(Searching.getting_group_choice)


@router.message(Command("settings"))
async def settings_command(message: Message):
    """
    Handling `settings` command
    :param message: */settings*
    """
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


@router.message(Command("my_schedule"))
@flags.chat_action(ChatAction.TYPING)
async def my_schedule_command(message: Message, state: FSMContext):
    """
    Handling `my_schedule` command
    :param message: */my_schedule*
    :param state:
    """
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
    """
    Handling `help` command
    :param message: */help*
    """
    answer = _("🤖 Список команд: \n")
    for cmd in bot_commands:
        answer += f"/{cmd.command} — {cmd.description}\n"
    await message.answer(answer)
