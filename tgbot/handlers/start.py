import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from tgbot.cb_data import StartMenuCallbackFactory
from tgbot.handlers.helpers import change_message_to_progress
from tgbot.keyboards.inline import create_start_choice_keyboard, create_study_divisions_keyboard
from tgbot.misc.states import SearchEducator
from tgbot.services.timetable_api.timetable_api import get_study_divisions

router = Router()


@router.message(commands=["start"])
async def bot_start_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    logging.info("start -- id:%s", message.from_user.id)
    await message.answer(
        text=("👋🏻 <b>Добро пожаловать, {name}!</b>\n"
              "ℹ️ Следуйте указаниям для настройки\n"
              "❕ Для корректной работы взаимодействуйте только с последним сообщением бота\n"
              "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
              "⬇️ Получить расписание по:").format(name=message.from_user.full_name),
        reply_markup=await create_start_choice_keyboard(),
    )
    # await db.add_new_user()


@router.callback_query(StartMenuCallbackFactory.filter(F.type == "student_navigation"))
async def student_navigation_callback(callback: CallbackQuery):
    await change_message_to_progress(callback.message)
    study_divisions = await get_study_divisions()
    await callback.message.edit_text(
        text=f"⬇️ Выберите направление: ",
        reply_markup=await create_study_divisions_keyboard(study_divisions)
    )
    await callback.answer(cache_time=2)


@router.callback_query(StartMenuCallbackFactory.filter(F.type == "educator_search"))
async def educator_search_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🧑‍🏫 Введите фамилию преподавателя:")
    await state.set_state(SearchEducator.getting_choice)


# @user_router.message(commands=["help"])
# async def bot_help_command(message: Message) -> None:
#     answer = "🤖 Список команд: \n"
#     commands = await bot.get_my_commands()
#     for cmd in commands:
#         answer += "/{command} — {description}\n".format(command=cmd['command'], description=cmd['description'])
#     await message.answer(answer)
