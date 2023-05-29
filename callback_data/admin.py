from enum import Enum

from aiogram.filters.callback_data import CallbackData


class DelAdmin(CallbackData, prefix="del_admin"):
    id: int


class Load(Enum):
    STOP_WORDS = 1
    DOCTORS = 2
    START = 3
    PHRASES = 4


class LoadList(CallbackData, prefix="load_list"):
    file: Load
