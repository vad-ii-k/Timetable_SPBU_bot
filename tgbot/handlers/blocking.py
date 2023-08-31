""" This module contains the code for handling chat member updates """
from aiogram import Router
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatMemberUpdated

from tgbot.services.db_api.db_commands import database

router = Router()


@router.my_chat_member()
async def my_chat_member_handler(update: ChatMemberUpdated):
    """
    This function handles the updates related to chat member status changes

    :param update:
    :return:
    """
    db_user = await database.get_user(update.from_user.id)
    if update.new_chat_member.status == ChatMemberStatus.KICKED:
        await db_user.update(is_bot_blocked=True).apply()
    elif update.new_chat_member.status == ChatMemberStatus.MEMBER:
        await db_user.update(is_bot_blocked=False).apply()
