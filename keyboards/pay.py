from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder

free_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Стандарт", callback_data="paytype_1"),
     InlineKeyboardButton(text="Премиум", callback_data="paytype_2")],
    [InlineKeyboardButton(text="Выход", callback_data="pay_exit")]
])

exit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="pay_exit")]
])


def pay(url: str) -> InlineKeyboardMarkup:
    mark = InlineKeyboardBuilder()
    mark.button(text="Оплатить подписку", url=url)
    mark.button(text="Проверить оплату",
                callback_data="check_pay")
    mark.button(text="Назад", callback_data="pay_call")
    mark.adjust(1)
    return mark.as_markup()
