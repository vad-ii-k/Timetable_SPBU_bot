from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender


class ConfigMessageMiddleware(BaseMiddleware):
    def __init__(self, config) -> None:
        self.config = config

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        data['config'] = self.config
        action = get_flag(data, "chat_action")
        if not action:
            return await handler(event, data)
        async with ChatActionSender(action=action, chat_id=event.chat.id):
            return await handler(event, data)


class ConfigCallbackMiddleware(BaseMiddleware):
    def __init__(self, config) -> None:
        self.config = config

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        data['config'] = self.config
        action = get_flag(data, "chat_action")
        if not action:
            return await handler(event, data)
        async with ChatActionSender(action=action, chat_id=event.message.chat.id):
            return await handler(event, data)
