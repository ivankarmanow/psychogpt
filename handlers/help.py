from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message as Msg

help = Router()


@help.message(Command("help"))
async def help_command(msg: Msg):
    await msg.answer("Тут будет помощь")
