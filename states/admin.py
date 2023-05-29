from aiogram.fsm.state import State, StatesGroup


class AddAdmin(StatesGroup):
    id = State()


class Mailing(StatesGroup):
    card = State()
    conf = State()


class File(StatesGroup):
    file = State()
