import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.cb_data import StudyDivisionCallbackFactory, StudyLevelCallbackFactory, ProgramCombinationsCallbackFactory, \
    AdmissionYearsCallbackFactory
from tgbot.data_classes import StudyLevel, ProgramCombination
from tgbot.handlers.helpers import change_message_to_progress
from tgbot.keyboards.inline import (
    create_start_choice_keyboard,
    create_study_divisions_keyboard,
    create_study_levels_keyboard,
    create_study_programs_keyboard,
    create_admission_years_keyboard, create_groups_keyboard
)
from tgbot.services.timetable_api.timetable_api import get_study_levels, get_study_divisions, get_groups

user_router = Router()


@user_router.message(commands=["start"])
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


@user_router.callback_query(text="student_navigation")
async def student_navigation_callback(callback: CallbackQuery):
    await change_message_to_progress(callback.message)
    study_divisions = await get_study_divisions()
    await callback.message.edit_text(
        text=f"⬇️ Выберите направление: ",
        reply_markup=await create_study_divisions_keyboard(study_divisions)
    )
    await callback.answer(cache_time=2)


@user_router.callback_query(StudyDivisionCallbackFactory.filter())
async def study_divisions_navigation_callback(
        callback: CallbackQuery, callback_data: StudyDivisionCallbackFactory, state: FSMContext
):
    await change_message_to_progress(callback.message)
    study_levels = await get_study_levels(callback_data.alias)
    await callback.message.edit_text(
        text="⬇️ Выберите уровень подготовки:",
        reply_markup=await create_study_levels_keyboard(study_levels)
    )
    await state.update_data(study_levels=study_levels)


@user_router.callback_query(StudyLevelCallbackFactory.filter())
async def study_levels_navigation_callback(
        callback: CallbackQuery, callback_data: StudyLevelCallbackFactory, state: FSMContext
):
    data = await state.get_data()
    study_level: StudyLevel = data["study_levels"][int(callback_data.serial)]
    await state.set_data({})
    await state.update_data(program_combinatons=study_level.program_combinations)

    await callback.message.edit_text(
        text="⬇️ Выберите программу подготовки: ",
        reply_markup=await create_study_programs_keyboard(study_level.program_combinations)
    )


@user_router.callback_query(ProgramCombinationsCallbackFactory.filter())
async def admission_years_navigation_callback(
        callback: CallbackQuery, callback_data: ProgramCombinationsCallbackFactory, state: FSMContext
):
    data = await state.get_data()
    program_combinaton: ProgramCombination = data["program_combinatons"][int(callback_data.serial)]
    await state.set_data({})

    await callback.message.edit_text(
        text="⬇️ Выберите год поступления: ",
        reply_markup=await create_admission_years_keyboard(program_combinaton.admission_years)
    )


@user_router.callback_query(AdmissionYearsCallbackFactory.filter())
async def group_choice_navigation_callback(callback: CallbackQuery, callback_data: AdmissionYearsCallbackFactory):
    await change_message_to_progress(callback.message)
    groups = await get_groups(callback_data.study_program_id)
    if len(groups) > 0:
        await callback.message.edit_text(
            text="⬇️ Выберите группу:",
            reply_markup=await create_groups_keyboard(groups)
        )
        # await GroupChoice.choosing.set()
    else:
        await callback.message.edit_text("❌ По данной программе группы не найдены!")


# @user_router.message(commands=["help"])
# async def bot_help_command(message: Message) -> None:
#     answer = "🤖 Список команд: \n"
#     commands = await bot.get_my_commands()
#     for cmd in commands:
#         answer += "/{command} — {description}\n".format(command=cmd['command'], description=cmd['description'])
#     await message.answer(answer)
