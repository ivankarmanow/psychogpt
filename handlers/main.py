import datetime
import random
import uuid

from aiogram import Bot, F, Router, flags
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext as FSM
from aiogram.types import CallbackQuery as Call
from aiogram.types import Message as Msg
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.sql.expression import func

import utils
from models import Answer, Name, StartQuestion, StopWord, User
from states.main import Main

router = Router()


@router.message(Command("restart"))
async def start_dialog(msg: Msg, state: FSM, session: Session, user: User):
    await msg.answer("Диалог начат заново")
    row = (await session.scalars(select(StartQuestion).order_by(func.random()))).first()
    await msg.answer(row.question)
    gender = 'мужчина' if user.gender.lower() == "м" else "женщина"
    names = (await session.scalars(select(Name.name))).all()
    await state.update_data(context=[{"role": "system", "content": f"Я {user.name}, {gender}, мне {user.age} лет. Отвечай как профессиональный психолог {random.choice(names)}. Помогай решить психологические проблемы, задавай уточняющие вопросы, поддерживай и утешай"}, {"role": "assistant", "content": row.question}])
    await state.set_state(Main.gpt)


@flags.chat_action('typing')
@router.message(Main.gpt, F.voice)
async def main_gpt_voice(msg: Msg, state: FSM, session: Session, user: User, bot: Bot):
    if user.pay != "premium" and user.pay != "trial":
        return await msg.answer("Чтобы общаться с ботом голосвыми сообщениями надо оплатить премиум подписку!")
    if msg.voice:
        file_id = msg.voice.file_id
    elif msg.audio:
        file_id = msg.audio.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    filename = f"{msg.from_user.id}-{uuid.uuid4()}.wav"
    msge = await msg.answer("Расшифровываю голосовое сообщение...")
    await bot.download_file(file_path, filename)
    prompt = await utils.transcribe(filename)
    await msge.edit_text(f"<b>Распознанный текст</b>👇\n{prompt}")
    await state.set_state(Main.gpt)
    if user.pay_to:
        if user.pay_to < datetime.datetime.now():
            user.pay = "free"
            await session.merge(user)
            await session.commit()
    if user.pay == "free":
        return await msg.answer("Ваша подписка закончилась. Оплатие доступ")
    if user.pay == "standart":
        words = await session.scalars(select(StopWord.word))
        if any(True for word in words if word.lower().strip() in prompt.lower().strip().split()):
            return await msg.answer("Прошу ввести корректный запрос или Попробуйте сформулировать запрос иначе, мы не поддерживаем беседы на данную тему")
    data = await state.get_data()
    gender = 'мужчина' if user.gender.lower() == "м" else "женщина"
    names = (await session.scalars(select(Name.name))).all()
    context = data.get("context", [{"role": "system", "content": f"Я {user.name}, {gender}, мне {user.age} лет. Отвечай как профессиональный психолог {random.choice(names)}. Помогай решить психологические проблемы, задавай уточняющие вопросы, поддерживай и утешай"}])
    if context[-1]["role"] == "user":
        return await msg.answer("Вы уже задали мне вопрос, пожалуйста, дождитесь моего ответа")
    context.append({"role": "user", "content": prompt})
    mesg = await msg.answer("⏳Пожалуйста, подождите немного, пока нейросеть обрабатывает ваш запрос...")
    context = await utils.generate_text(context)
    await state.update_data(context=context)
    answers = (await session.scalars(select(Answer).where(Answer.user_id == msg.from_user.id).order_by(Answer.id))).all()
    if len(answers) > 10:
        for answer in answers[:10-len(answers)]:
            await session.delete(answer)
    session.add(Answer(user_id=msg.from_user.id,
                question=prompt, answer=context[-1]["content"]))
    await session.commit()
    await mesg.edit_text(context[-1]["content"])


@flags.chat_action('typing')
@router.message(Main.gpt, F.text)
async def main_gpt(msg: Msg, state: FSM, session: Session, user: User):
    await state.set_state(Main.gpt)
    if user.pay_to:
        if user.pay_to < datetime.datetime.now():
            user.pay = "free"
            await session.merge(user)
            await session.commit()
    if user.pay == "free":
        return await msg.answer("Ваша подписка закончилась. Оплатие доступ")
    prompt = msg.text
    if user.pay == "standart":
        words = await session.scalars(select(StopWord.word))
        if any(True for word in words if word.lower().strip() in prompt.lower().strip().split()):
            return await msg.answer("Прошу ввести корректный запрос или Попробуйте сформулировать запрос иначе, мы не поддерживаем беседы на данную тему")
    data = await state.get_data()
    gender = 'мужчина' if user.gender.lower() == "м" else "женщина"
    names = (await session.scalars(select(Name.name))).all()
    context = data.get("context", [{"role": "system", "content": f"Я {user.name}, {gender}, мне {user.age} лет. Отвечай как профессиональный психолог {random.choice(names)}. Помогай решить психологические проблемы, задавай уточняющие вопросы, поддерживай и утешай"}])
    if context[-1]["role"] == "user":
        return await msg.answer("Вы уже задали мне вопрос, пожалуйста, дождитесь моего ответа")
    context.append({"role": "user", "content": prompt})
    mesg = await msg.answer("⏳Пожалуйста, подождите немного, пока нейросеть обрабатывает ваш запрос...")
    context = await utils.generate_text(context)
    await state.update_data(context=context)
    answers = (await session.scalars(select(Answer).where(Answer.user_id == msg.from_user.id).order_by(Answer.id))).all()
    if len(answers) > 10:
        for answer in answers[:10-len(answers)]:
            await session.delete(answer)
    session.add(Answer(user_id=msg.from_user.id,
                question=prompt, answer=context[-1]["content"]))
    await session.commit()
    await mesg.edit_text(context[-1]["content"])
