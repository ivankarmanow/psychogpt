from aiogram.fsm.state import State, StatesGroup


class Pay(StatesGroup):
    select = State()
    check = State()
