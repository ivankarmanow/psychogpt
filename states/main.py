from aiogram.fsm.state import StatesGroup, State


class Main(StatesGroup):
    gpt = State()
