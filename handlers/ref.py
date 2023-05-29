from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message as Msg

ref = Router()


@ref.message(Command("ref"))
async def _ref(msg: Msg):
    await msg.answer(f"Твоя реферальная ссылка - https://t.me/one_psychology_bot?start=r{msg.from_user.id}\nКаждый пользователь, зарегистрировавшийся по твоей ссылке, добавляет тебе 1 сутки к подписке")
