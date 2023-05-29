from aiogram.filters.callback_data import CallbackData


class Age(CallbackData, prefix="age"):
    age: int
