import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.utils.chat_action import ChatActionMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import config
import models
from handlers import admin, help, pay, profile, ref, router, start
from middlewares import (ClearMiddleware, DbSessionMiddleware,
                         MessageToCallbacksMiddleware)


class CustomFormatter(logging.Formatter):

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fmt = "%(asctime)s %(filename)s[%(lineno)d]: %(message)s"
    hndl = logging.StreamHandler()
    hndl.setLevel(logging.INFO)
    hndl.setFormatter(CustomFormatter(fmt))
    logger.addHandler(hndl)


async def setup_db():
    engine = create_async_engine(url=config.DB_URL)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        # await conn.run_sync(db.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)
    return sessionmaker


async def main():

    setup_logger()
    sessionmaker = await setup_db()

    bot = Bot(token=config.BOT_TOKEN, parse_mode='HTML')
    dp = Dispatcher(storage=MemoryStorage())

    # dp.include_router(admin)
    dp.include_routers(start, admin, help, ref, profile, pay, router)

    await bot.delete_webhook(drop_pending_updates=True)

    dp.update.outer_middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.callback_query.middleware(CallbackAnswerMiddleware())
    dp.callback_query.middleware(MessageToCallbacksMiddleware())
    dp.message.middleware(ChatActionMiddleware())
    dp.update.middleware(ClearMiddleware())

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
