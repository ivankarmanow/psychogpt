import logging
from typing import *

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, TelegramObject)
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.future import select

import config
import models


class MessageToCallbacksMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        data['msg'] = event.message
        return await handler(event, data)


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            user_id = event.message.from_user.id if event.event_type == "message" else event.callback_query.from_user.id
            data['user'] = await session.scalar(select(models.User).where(models.User.id == user_id))
            return await handler(event, data)


class ClearMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        clear = get_flag(data, "clear")
        if not clear:
            return await handler(event, data)
        else:
            await data['state'].clear()
            return await handler(event, data)
