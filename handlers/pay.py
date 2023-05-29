import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext as FSM
from aiogram.types import CallbackQuery as Call
from aiogram.types import Message as Msg
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.sql.expression import func

import config
import utils
from keyboards import pay as kb
from models import User
from states.main import Main
from states.pay import Pay

pay = Router()


@pay.message(Command('pay'))
async def _pay(msg: Msg, state: FSM, user: User):
    if user.pay == "standart":
        pay_status = "стандартная"
    elif user.pay == "premium":
        pay_status = "премиум"
    elif user.pay == "trial":
        pay_status = "пробная"
    else:
        pay_status = "ограниченная"
    if user.pay != "free":
        await msg.answer(f"У вас {pay_status} подписка до {user.pay_to}. Вы можете продлить её, приведя друга по ссылке (команда /ref) (+1 день к подписке)")
    else:
        await msg.answer(f"Ваша подписка закончилась. Чтобы продолжить использовать бота, оплатите стандартную, либо премиум подписку\nСтандартная подписка - {config.prices['standart']} рублей в месяц\nПозволяет использовать бота, но имеет ограничения: только текстовые запросы, фильтр тем\nПремиум - {config.prices['premium']} рублей в месяц\nСнимает все ограничения стандартной подписки", reply_markup=kb.free_pay)
        await state.set_state(Pay.select)


@pay.callback_query(F.data == "pay_call")
async def _pay_call(call: Call, msg: Msg, state: FSM, user: User):
    if user.pay == "standart":
        pay_status = "стандартная"
    elif user.pay == "premium":
        pay_status = "премиум"
    elif user.pay == "trial":
        pay_status = "пробная"
    else:
        pay_status = "ограниченная"
    if user.pay != "free":
        await msg.edit_text(f"У вас {pay_status} подписка до {user.pay_to}. Вы можете продлить её, приведя друга по ссылке (команда /ref) (+1 день к подписке)")
    else:
        await msg.edit_text(f"Ваша подписка закончилась. Чтобы продолжить использовать бота, оплатите стандартную, либо премиум подписку\nСтандартная подписка - {config.prices['standart']} рублей в месяц\nПозволяет использовать бота, но имеет ограничения: только текстовые запросы, фильтр тем\nПремиум - {config.prices['premium']} рублей в месяц\nСнимает все ограничения стандартной подписки", reply_markup=kb.free_pay)
        await state.set_state(Pay.select)


@pay.callback_query(F.data.startsith("paytype"), Pay.select)
async def select_pay(call: Call, msg: Msg, state: FSM, user: User):
    if user.pay != "free":
        await msg.answer("У вас уже оплачена подписка", reply_markup=kb.exit)
        return await state.set_state(Main.gpt)
    sel = call.data.split("_")[-1]
    invoice = utils.create_invoice(sel)
    await state.set_state(Pay.check)
    await state.update_data(invoice=invoice, sel=sel)
    await msg.edit_text(f"Оплатите {invoice['amount']} рублей", reply_markup=kb.pay(invoice['url']))


@pay.callback_query(Pay.check, F.data == "check_pay")
async def check_pay(call: Call, msg: Msg, state: FSM, user: User, session: Session):
    data = await state.get_data()
    invoice = data.get("invoice")
    sel = data.get("sel")
    if invoice:
        if utils.check_pay(invoice['id']):
            if sel == "1":
                user.pay = "standart"
                user.pay_to = datetime.date.today() + datetime.timedelta(days=30)
            elif sel == "2":
                user.pay = "premium"
                user.pay_to = datetime.date.today() + datetime.timedelta(days=30)
            else:
                user.pay = "free"
            await session.merge(user)
            await session.commit()
            # await state.set_state(Main.gpt)
            await msg.edit_text("Подпика оплачена", reply_markup=kb.exit)
        else:
            return await msg.answer("Ты ещё не оплатил подписку!")
