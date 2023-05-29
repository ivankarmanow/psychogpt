from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder

from callback_data.profile import Age

menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Изменить имя", callback_data="change_name")],
    [InlineKeyboardButton(text="Изменить возраст", callback_data="change_age")],
    [InlineKeyboardButton(text="Изменить пол", callback_data="change_gender")],
    [InlineKeyboardButton(text="Выйти", callback_data="exit")],
])

exit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="profile_menu")]
])


gender = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Мужской", callback_data="gen1"), InlineKeyboardButton(text="Женский", callback_data="gen0")]
])


def age(age):
    mark = InlineKeyboardBuilder()
    if age <= 18:
        mark.button(text="18", callback_data="18")
        mark.button(text=">", callback_data=Age(age=19).pack())
        mark.button(text="Выбрать", callback_data="select_age")
        mark.button(text="Назад", callback_data="profile_menu")
        mark.adjust(2, 1, 1)
    else:
        mark.button(text="<", callback_data=Age(age=age-1).pack())
        mark.button(text=str(age), callback_data=str(age))
        mark.button(text=">", callback_data=Age(age=age+1).pack())
        mark.button(text="Выбрать", callback_data="select_age")
        mark.button(text="Назад", callback_data="profile_menu")
        mark.adjust(3, 1, 1)
    return mark.as_markup()