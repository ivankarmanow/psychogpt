import datetime
import random

from aiogram import F, Router, Bot
from aiogram.types import Message as Msg, CallbackQuery as Call, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext as FSM
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.sql.expression import func

from callback_data.start import Age
from keyboards import start as kb
from models import User, StartQuestion, Name
from states.start import Reg
from states.main import Main

start = Router()


@start.message(Command("start"))
async def _start(msg: Msg, state: FSM, session: Session):
    if not await session.scalar(exists().where(User.id == msg.from_user.id).select()):
        await msg.answer("Привет👋\nВсе диалоги строго конфиденциальны, к ним не имеют доступ разработчики")
        await msg.answer("Как к тебе обращаться?", reply_markup=kb.name(msg.from_user.full_name))
        await state.set_state(Reg.name)
        if len(msg.text.split(maxsplit=1)) > 1:
            try:
                await state.update_data(ref=int(msg.text.split(maxsplit=1)[1][1:]))
            except:
                pass
    else:
        await msg.answer("Мы с тобой уже знакомы, если хочешь поменять свои данные, воспользуйся командой /profile")


@start.message(Reg.name)
async def name(msg: Msg, state: FSM):
    await state.update_data(name=msg.text)
    await msg.answer("Выберите пол", reply_markup=kb.gender)
    await state.set_state(Reg.gender)


@start.callback_query(Reg.gender, F.data.startswith("gen"))
async def gender(call: Call, state: FSM):
    await state.update_data(gender=call.data[3])
    await call.message.answer("Введите свой возраст используя клавиатуру", reply_markup=kb.age(25))
    await state.set_state(Reg.age)


@start.callback_query(Age.filter(F.age), Reg.age)
async def age_change(call: Call, state: FSM, callback_data: Age, msg: Msg):
    await state.update_data(age=int(callback_data.age))
    try:
        await msg.edit_reply_markup(reply_markup=kb.age(callback_data.age))
    except:
        pass


@start.callback_query(Reg.age, F.data == "select_age")
async def select_age(call: Call, state: FSM, msg: Msg, session: Session, bot: Bot):
    data = await state.get_data()
    print(data)
    if not await session.scalar(exists().where(User.id == call.from_user.id).select()):
        days = 2 if data.get("ref") else 1
        user = User(
            id=call.from_user.id,
            name=data.get("name"),
            age=data.get("age"),
            gender=data.get("gender"),
            pay="trial",
            pay_to=datetime.datetime.now() + datetime.timedelta(days=days)
        )
        session.add(user)
        await session.commit()
        if data.get("ref"):
            ref = await session.get(User, int(data.get("ref")))
            if ref.pay_to < datetime.datetime.now():
                ref.pay = "trial"
                ref.pay_to = datetime.datetime.now() + datetime.timedelta(days=1)
                await bot.send_message(ref.id, f"По вашей ссылке зарегистрировался другой пользователь, ваша пробная подписка продлена на 1 день")
            else:
                ref.pay_to = ref.pay_to + datetime.timedelta(days=1)
                await bot.send_message(ref.id, f"По вашей ссылке зарегистрировался другой пользователь, ваша подписка продлена на 1 день")
            await session.commit()
    row = (await session.scalars(select(StartQuestion).order_by(func.random()))).first()
    await msg.answer(row.question, reply_markup=ReplyKeyboardRemove())
    gender = 'мужчина' if user.gender.lower() == "м" else "женщина"
    names = (await session.scalars(select(Name.name))).all()
    await state.update_data(context=[{"role": "system", "content": f"Я {user.name}, {gender}, мне {user.age} лет. Отвечай как профессиональный психолог {random.choice(names)}. Помогай решить психологические проблемы, задавай уточняющие вопросы, поддерживай и утешай"}, {"role": "assistant", "content": row.question}])
    await state.set_state(Main.gpt)
