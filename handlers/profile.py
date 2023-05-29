from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext as FSM
from aiogram.types import CallbackQuery as Call
from aiogram.types import Message as Msg
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.sql.expression import func

from callback_data.profile import Age
from keyboards import profile as kb
from models import User
from states.main import Main
from states.profile import Change

profile = Router()


@profile.message(Command('profile'))
async def _profile(msg: Msg, state: FSM, session: Session, user: User):
    gender = "мужчина" if user.gender == "1" else "женщина"
    if user.pay == "standart":
        pay = "стандартная"
    elif user.pay == "premium":
        pay = "премиум"
    elif user.pay == "trial":
        pay = "пробная"
    else:
        pay = "ограниченная"
    await state.set_state(Change.menu)
    await msg.answer(f"""Тебя зовут {user.name}
Тебе {user.age} лет
Ты {gender}
У тебя {pay} подписка до {user.pay_to.strftime("%d.%m.%Y")}""", reply_markup=kb.menu)


@profile.callback_query(F.data == "profile_menu")
async def _profile_call(call: Call, msg: Msg, state: FSM, user: User):
    gender = "мужчина" if user.gender == 1 else "женщина"
    if user.pay == "standart":
        pay = "стандартная"
    elif user.pay == "premium":
        pay = "премиум"
    elif user.pay == "trial":
        pay = "пробная"
    else:
        pay = "ограниченная"
    await state.set_state(Change.menu)
    await msg.edit_text(f"""Тебя зовут {user.name}
Тебе {user.age} лет
Ты {gender}
У тебя {pay} подписка до {user.pay_to.strftime("%d.%m.%Y")}""", reply_markup=kb.menu)


@profile.callback_query(F.data == "exit")
async def _menu(call: Call, state: FSM):
    await state.set_state(Main.gpt)
    await call.message.edit_text("Можешь продолжать общение с ботом, переписка сохранена")


@profile.callback_query(F.data == "change_name")
async def name(call: Call, msg: Msg, state: FSM, user: User):
    await state.set_state(Change.name)
    await msg.edit_text(f"Отправь мне имя, которое хочешь установить. Сейчас я зову тебя {user.name}", reply_markup=kb.exit)


@profile.message(Change.name)
async def change_name(msg: Msg, state: FSM, user: User, session: Session):
    user.name = msg.text
    await session.merge(user)
    await session.commit()
    await state.set_state(Change.menu)
    await msg.answer(f"Отлично, я поменял тебе имя на {msg.text}", reply_markup=kb.exit)


@profile.callback_query(F.data == "change_age")
async def age(call: Call, msg: Msg, state: FSM, user: User):
    await state.set_state(Change.age)
    await msg.edit_text(f"Сейчас я считаю, что тебе {user.age} лет. Введи новый возраст", reply_markup=kb.age(user.age))


@profile.callback_query(Age.filter(F.age), Change.age)
async def age_change(call: Call, state: FSM, callback_data: Age, msg: Msg):
    await state.update_data(age=int(callback_data.age))
    try:
        await msg.edit_reply_markup(reply_markup=kb.age(callback_data.age))
    except:
        pass


@profile.callback_query(Change.age, F.data == "select_age")
async def age(call: Call, msg: Msg, state: FSM, user: User, session: Session):
    await state.set_state(Change.menu)
    user.age = (await state.get_data())["age"]
    await session.merge(user)
    await session.commit()
    await msg.edit_text(f"Возраст обновлён", reply_markup=kb.exit)


@profile.callback_query(F.data == "change_gender")
async def gender(call: Call, msg: Msg, state: FSM, user: User):
    await state.set_state(Change.gender)
    await msg.edit_text("Выбери пол, который хочешь установить", reply_markup=kb.gender)


@profile.callback_query(F.data.startswith("gen"), Change.gender)
async def change_gender(call: Call, msg: Msg, state: FSM, user: User, session: Session):
    user.gender = call.data[-1]
    await session.merge(user)
    await session.commit()
    await state.set_state(Change.menu)
    await msg.edit_text("Пол обновлён", reply_markup=kb.exit)
