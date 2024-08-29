""" Handling related to settings """

import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from tgbot.handlers.commands import settings_command
from tgbot.handlers.helpers import delete_message
from tgbot.keyboards.inline import create_settings_daily_summary_keyboard, create_settings_keyboard
from tgbot.misc.cb_data import (
    ScheduleSubscriptionCallbackFactory,
    SettingsCallbackFactory,
    SettingsDailySummaryCallbackFactory,
)
from tgbot.services.db_api.db_commands import database

router = Router()


@router.callback_query(SettingsCallbackFactory.filter(F.type == "daily_summary"))
async def daily_summary_callback(callback: CallbackQuery):
    """
    Setting the time for the daily summary, sends a keyboard with parameters for notification
    :param callback:
    """
    user = await database.get_user(tg_user_id=callback.from_user.id)
    main_schedule = await database.get_main_schedule(user_id=user.user_id)

    if main_schedule:
        settings = await database.get_settings_by_tg_id(tg_user_id=callback.from_user.id)
        await callback.message.edit_text(
            text=_(
                "⚙️<b> Выберите время для получения\n"
                "ㅤㅤ сводки расписания на день</b>\n"
                "Заранее вечером в ┃ В день занятий в"
            ),
            reply_markup=await create_settings_daily_summary_keyboard(settings.daily_summary),
        )
        await callback.answer(cache_time=1)
    else:
        await callback.answer(
            text=_("⚠️ Для настройки уведомлений необходимо наличие основного расписания"),
            show_alert=True,
            cache_time=1,
        )


@router.callback_query(SettingsDailySummaryCallbackFactory.filter())
async def settings_daily_summary_callback(callback: CallbackQuery, callback_data: SettingsDailySummaryCallbackFactory):
    """
    Handling the time selection button for the daily summary
    :param callback:
    :param callback_data:
    """
    settings = await database.get_settings_by_tg_id(tg_user_id=callback.from_user.id)
    if callback_data.choice != "back":
        value = datetime.time(int(callback_data.choice)) if callback_data.choice != "disabling" else None
        await settings.update(daily_summary=value).apply()
        await callback.answer(text=_("Настройки обновлены ✅"), show_alert=False)
    await callback.message.delete()
    await settings_command(callback.message)


@router.callback_query(SettingsCallbackFactory.filter(F.type == "schedule_view"))
async def settings_view_callback(callback: CallbackQuery):
    """
    Handling changes to the default schedule view
    :param callback:
    """
    settings = await database.get_settings_by_tg_id(tg_user_id=callback.from_user.id)
    await settings.update(schedule_view_is_picture=not settings.schedule_view_is_picture).apply()
    await callback.message.edit_reply_markup(reply_markup=await create_settings_keyboard(settings))
    await callback.answer(text=_("Настройки обновлены ✅"), show_alert=False)


@router.callback_query(SettingsCallbackFactory.filter(F.type == "language"))
async def settings_language_callback(callback: CallbackQuery):
    """
    Handling language changes
    :param callback:
    """
    settings = await database.get_settings_by_tg_id(tg_user_id=callback.from_user.id)
    await settings.update(language="en" if settings.language == "ru" else "ru").apply()
    await callback.answer(
        text=_("The language has been successfully changed to 🇬🇧\n" "Messages will now be sent in English"),
        show_alert=True,
    )
    await callback.message.delete()


@router.callback_query(ScheduleSubscriptionCallbackFactory.filter())
async def schedule_subscription_callback(
    callback: CallbackQuery, callback_data: ScheduleSubscriptionCallbackFactory, state: FSMContext
):
    """
    Handling subscription selection for a schedule
    :param callback:
    :param callback_data:
    :param state:
    """
    if callback_data.answer:
        data = await state.get_data()
        await database.set_main_schedule(
            tg_user_id=callback.from_user.id,
            tt_id=int(data.get("tt_id")),
            user_type=data.get("user_type"),
            schedule_name=data.get("schedule_name"),
        )
        instruction = await callback.message.answer(
            _(
                "Вы подписались на расписание! ✅\n"
                "Воспользуйтесь командой:\n"
                "— /my_schedule для просмотра своего основного расписания\n"
                "— /settings для настройки уведомлений"
            )
        )
        await callback.message.delete()
        await delete_message(instruction, 60)
        await state.set_data({})
    else:
        await callback.answer(text=_("Вы отказались от подписки! ❌"), show_alert=False)
        await callback.message.delete()
