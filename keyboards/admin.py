from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.future import select

from callback_data.admin import *
from models import User
from states.admin import *

admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📈 Статистика",
                          callback_data="stats")],
    [InlineKeyboardButton(text="✉️ Рассылка",
                          callback_data="admin_mailing")],
    [InlineKeyboardButton(text="🔑 Админы",
                          callback_data="conf_admins")],
    [InlineKeyboardButton(text="Стоп-слова",
                          callback_data=LoadList(file=Load.STOP_WORDS).pack())],
    [InlineKeyboardButton(text="Психологи",
                          callback_data=LoadList(file=Load.DOCTORS).pack())],
    [InlineKeyboardButton(text="Стартовые вопросы",
                          callback_data=LoadList(file=Load.START).pack())],
    [InlineKeyboardButton(text="Вставки в запрос",
                          callback_data=LoadList(file=Load.PHRASES).pack())],
])

back_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="⏪ Назад в админку", callback_data="admin")]
])


async def back(data: str = "menu") -> InlineKeyboardMarkup:
    mark = [[InlineKeyboardButton(
        text="◀️ Назад", callback_data=data)]]
    return InlineKeyboardMarkup(inline_keyboard=mark)

admins_kb = [
    [InlineKeyboardButton(text="➕ Добавить админа",
                          callback_data="add_admin")],
    [InlineKeyboardButton(
        text="➖ Удалить админа", callback_data="del_admin")],
    [InlineKeyboardButton(
        text="⏪ Вернуться в админку", callback_data="admin")]
]
admins_kb = InlineKeyboardMarkup(inline_keyboard=admins_kb)


async def del_admins_kb(session: Session, bot):
    admins = await session.scalars(select(User.id).where(User.is_admin == True))
    mark = InlineKeyboardBuilder()
    for i in admins:
        chat = await bot.get_chat(i)
        mark.button(text=chat.full_name, callback_data=DelAdmin(id=i).pack())
    mark.button(text="⏪ Назад", callback_data="conf_admins")
    mark.adjust(1)
    return mark.as_markup()


mailing_conf = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Да", callback_data="mailing_conf_yes"),
     InlineKeyboardButton(text="Нет", callback_data="admin_mailing")],
    [InlineKeyboardButton(text="⏪ Назад",
                          callback_data="admin_mailing")]
])
