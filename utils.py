import asyncio
import logging
import os
import subprocess
from typing import Union

import openai
from aiogram import types
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import config
from crystalpay import CrystalPAY, InvoiceType

openai.api_key = config.OPENAI_TOKEN
PAY = CrystalPAY(*list(config.PAY.values()))


async def generate_text(context: list = [], model="gpt-3.5-turbo") -> dict:
    try:
        if model == "gpt-3.5-turbo":
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=context
            )
            context.append(
                {"role": "assistant", "content": response['choices'][0]['message']['content']})
            return context
        elif model == "text-davinci-003":
            response = await openai.Completion.acreate(
                model="text-davinci-003",
                prompt="Write program, that will print 'Hello World!' to console"
            )
            result = response['choices'][0]['text']
            return result
        else:
            return Exception("Такой модели не существует")
    except Exception as e:
        logging.error(e)
        return False


def get_arg(msg: Message) -> str:
    txt = msg.text.strip().split(" ", maxsplit=1)
    if len(txt) > 1:
        return txt[1]
    else:
        return ""


async def transcribe(filename: str) -> str:
    old_filename = filename
    filename = filename.replace(".wav", ".mp3")
    command = [
        'ffmpeg',
        '-i', old_filename,
        '-codec:a', 'libmp3lame',
        '-nostdin',
        filename
    ]
    proc = subprocess.Popen(command)
    proc.wait()
    with open(filename, "rb") as audio:
        result = await openai.Audio.atranscribe("whisper-1", audio)
    os.remove(filename)
    os.remove(old_filename)
    return result.text


def create_invoice(selected: int) -> dict:
    try:
        selected = int(selected)
    except ValueError:
        logging.error(e)
        return {"error" - 2}
    if selected == 1:
        amount = config.prices['standart']
    elif selected == 2:
        amount = config.prices['premium']
    else:
        raise ValueError("Нет такого типа подписки")
    try:
        invoice = PAY.Invoice.create(
            amount=amount,
            type_=InvoiceType.purchase,
            lifetime=15
        )
        return invoice
    except Exception as e:
        logging.error(e)
        return {"error": -1}


def check_invoice(id: str) -> bool:
    try:
        result = PAY.Invoice.getinfo(id=id)
        if result['state'] == 'payed':
            return True
        else:
            return False
    except Exception as e:
        logging.error(e)
        return False
