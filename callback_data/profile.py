from aiogram.filters.callback_data import CallbackData


class Age(CallbackData, prefix="edit_age"):
    age: int
