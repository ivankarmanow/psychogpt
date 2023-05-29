from aiogram.fsm.state import State, StatesGroup


class Change(StatesGroup):
    menu = State()
    name = State()
    age = State()
    gender = State()
