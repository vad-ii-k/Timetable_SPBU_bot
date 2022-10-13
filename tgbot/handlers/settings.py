import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from tgbot.cb_data import (
    SettingsCallbackFactory,
    SettingsDailySummaryCallbackFactory,
    ScheduleSubscriptionCallbackFactory,
)
from tgbot.handlers.commands import settings_command
from tgbot.handlers.helpers import _delete_message
from tgbot.keyboards.inline import create_settings_daily_summary_keyboard, create_settings_keyboard
from tgbot.services.db_api.db_commands import database

router = Router()


@router.callback_query(SettingsCallbackFactory.filter(F.type == "daily_summary"))
async def daily_summary_callback(callback: CallbackQuery):
    user = await database.get_user(tg_user_id=callback.from_user.id)
    settings = await database.get_settings(user)
    await callback.message.edit_text(
        text=_("⚙️<b> Выберите время для получения\n"
               "ㅤㅤ сводки расписания на день</b>\n"
               "Заранее вечером в ┃ В день занятий в"),
        reply_markup=await create_settings_daily_summary_keyboard(settings.daily_summary)
    )
    await callback.answer(cache_time=1)


@router.callback_query(SettingsDailySummaryCallbackFactory.filter())
async def settings_daily_summary_callback(callback: CallbackQuery, callback_data: SettingsDailySummaryCallbackFactory):
    user = await database.get_user(tg_user_id=callback.from_user.id)
    settings = await database.get_settings(user)
    if callback_data.choice != "back":
        value = datetime.time(int(callback_data.choice)) if callback_data.choice != "disabling" else None
        await settings.update(daily_summary=value).apply()
        await callback.answer(text=_("Настройки обновлены ✅"), show_alert=False)
    await callback.message.delete()
    await settings_command(callback.message)


@router.callback_query(SettingsCallbackFactory.filter(F.type == "schedule_view"))
async def settings_view_callback(callback: CallbackQuery):
    user = await database.get_user(tg_user_id=callback.from_user.id)
    settings = await database.get_settings(user)
    await settings.update(schedule_view_is_picture=not settings.schedule_view_is_picture).apply()
    await callback.message.edit_reply_markup(reply_markup=await create_settings_keyboard(settings))
    await callback.answer(text=_("Настройки обновлены ✅"), show_alert=False)


@router.callback_query(SettingsCallbackFactory.filter(F.type == "language"))
async def settings_language_callback(callback: CallbackQuery):
    user = await database.get_user(tg_user_id=callback.from_user.id)
    settings = await database.get_settings(user)
    await settings.update(language='en' if settings.language == 'ru' else 'ru').apply()
    await callback.answer(
        text=_("The language has been successfully changed to 🇬🇧\n"
               "Messages will now be sent in English"),
        show_alert=True
    )
    await callback.message.delete()


@router.callback_query(ScheduleSubscriptionCallbackFactory.filter())
async def schedule_subscription_callback(
        callback: CallbackQuery, callback_data: ScheduleSubscriptionCallbackFactory, state: FSMContext
):
    if callback_data.answer:
        data = await state.get_data()
        await database.set_main_schedule(
            tg_user_id=callback.from_user.id,
            tt_id=int(data.get("tt_id")),
            user_type=data.get("user_type"),
            schedule_name=data.get("schedule_name")
        )
        instruction = await callback.message.answer(
            text=_("Вы подписались на расписание! ✅\n"
                   "Воспользуйтесь командой:\n"
                   "— /my_schedule для просмотра своего основного расписания\n"
                   "— /settings для настройки уведомлений")
        )
        await callback.message.delete()
        await _delete_message(instruction, 20)
        await state.set_data({})
    else:
        await callback.message.delete()
        await callback.answer(text=_("Вы отказались от подписки! ❌"), show_alert=False)
