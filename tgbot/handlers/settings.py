from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from magic_filter import F

from tgbot.cb_data import SettingsCallbackFactory
from tgbot.keyboards.inline import create_settings_daily_summary_keyboard
from tgbot.services.db_api.db_commands import database

router = Router()


@router.callback_query(SettingsCallbackFactory.filter(F.type == "daily_summary"))
async def daily_summary_callback(callback: CallbackQuery):
    user = await database.get_user(tg_user=callback.from_user)
    settings = await database.get_settings(user)
    await callback.message.edit_text(
        text=_("⚙️<b> Выберите время для получения\n"
               "ㅤㅤ сводки расписания на день</b>\n"
               "Заранее вечером в ┃ В день занятий в"),
        reply_markup=await create_settings_daily_summary_keyboard(settings.daily_summary)
    )
    await callback.answer(cache_time=1)
