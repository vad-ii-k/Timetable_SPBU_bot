import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from tgbot.keyboards.inline import create_start_choice_keyboard, create_settings_keyboard
from tgbot.misc.states import SearchEducator, SearchGroup
from tgbot.services.db_api.db_commands import database

router = Router()


@router.message(commands=["start"], state="*")
async def start_command(message: Message, state: FSMContext) -> None:
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
    await database.add_new_user(tg_user=message.from_user)


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
    user = await database.get_user(tg_user=message.from_user)
    settings = await database.get_settings(user)

    text = _("📅 Основное расписание:\n — ")
    # Добавить получение расписания
    text += _("\n\n⚙️ Текущие настройки:")
    await message.answer(text=text, reply_markup=await create_settings_keyboard(settings))


# @user_router.message(commands=["help"])
# async def bot_help_command(message: Message) -> None:
#     answer = "🤖 Список команд: \n"
#     commands = await bot.get_my_commands()
#     for cmd in commands:
#         answer += "/{command} — {description}\n".format(command=cmd['command'], description=cmd['description'])
#     await message.answer(answer)
