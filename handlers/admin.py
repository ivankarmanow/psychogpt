import asyncio
import logging
from typing import List

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.filters import MagicData as D
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, InputMediaPhoto, InputMediaVideo,
                           Message)
from aiogram_media_group import media_group_handler
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.sql.expression import func

import keyboards.admin as kb
from callback_data.admin import *
from models import User
from states.admin import *

admin = Router()
admin.message.filter(D(F.user.is_admin))
admin.callback_query.filter(D(F.user.is_admin))


@admin.message(Command('admin'))
async def admin_menu(message: Message,  state: FSMContext):
    await state.clear()
    await message.answer("Админка", reply_markup=kb.admin_kb)


@admin.callback_query(F.data == "admin")
async def iadm(call: CallbackQuery, msg: Message, state: FSMContext):
    await msg.edit_text("Админка", reply_markup=kb.admin_kb)
    await state.clear()


@admin.callback_query(F.data == "stats")
async def stats(call: CallbackQuery, state: FSMContext, msg: Message, session: Session):
    users = await session.scalar(select(func.count()).select_from(User))
    await msg.edit_text("Пользователей бота: {}".format(users), reply_markup=kb.back_admin)


@admin.callback_query(F.data == "admin_mailing")
async def admin_mailing(call: CallbackQuery, state: FSMContext, msg: Message, session: Session):
    await state.set_state(Mailing.card)
    await msg.edit_text("Теперь отправьте сообщение которое хотите разослать", reply_markup=kb.back_admin)


@admin.message(F.media_group_id, Mailing.card)
@media_group_handler
async def admin_mailing_media(msgs: List[Message], state: FSMContext, session: Session, bot):
    await state.update_data(txt=msgs[0].caption)
    media = []
    for msg in msgs:
        if msg.content_type == "photo":
            media.append({
                "file_id": msg.photo[-1].file_id,
                "type": "photo"
            })
        elif msg.content_type == "video":
            media.append({
                "file_id": msg.video.file_id,
                "type": "video"
            })
    await state.update_data(media=media)
    await state.set_state(Mailing.conf)
    await msgs[0].answer("Вы точно хотите разослать это сообщение?", reply_markup=kb.mailing_conf)


@admin.message(F.photo, Mailing.card)
@admin.message(F.video, Mailing.card)
async def admin_mailing_media_other(msg: Message, state: FSMContext, session: Session):
    await state.update_data(txt=msg.caption)
    if msg.content_type == "photo":
        media = [{
            "file_id": msg.photo[-1].file_id,
            "type": "photo"
        }]
    elif msg.content_type == "video":
        media = [{
            "file_id": msg.video.file_id,
            "type": "video"
        }]
    await state.update_data(media=media)
    await state.set_state(Mailing.conf)
    await msg.answer("Вы точно хотите разослать это сообщение?", reply_markup=kb.mailing_conf)


@admin.message(Mailing.card)
async def admin_mailing_text(msg: Message, state: FSMContext, session: Session):
    await state.update_data(txt=msg.text)
    await state.set_state(Mailing.conf)
    await msg.answer("Вы точно хотите разослать это сообщение?", reply_markup=kb.mailing_conf)


@admin.callback_query(Mailing.conf, F.data == "mailing_conf_yes")
async def broadcast_users(call: CallbackQuery, msg: Message, state: FSMContext, session: Session, bot: Bot):
    data = await state.get_data()
    users = (await session.scalars(
        select(User.id)
    )).all()
    mesg = await msg.edit_text(f"Рассылка по {len(users)} пользователям...")
    media = data.get("media", [])
    txt = data.get("txt", "")
    count = 0
    err = 0
    for user in users:
        try:
            if len(media) < 1:
                await bot.send_message(user, txt)
            elif len(media) == 1:
                if media[0]['type'] == "video":
                    await bot.send_video(user, media[0]['file_id'], txt)
                elif media[0]['type'] == "photo":
                    await bot.send_photo(user, media[0]['file_id'], txt)
            else:
                mdg = []
                for med in media:
                    if med['type'] == "video":
                        mdg.append(InputMediaVideo(media=med['file_id']))
                    elif med['type'] == "photo":
                        mdg.append(InputMediaPhoto(media=med['file_id']))
                mdg[0].caption = txt
                await bot.send_media_group(user, mdg)
                await asyncio.sleep(0.05)
        except Exception as e:
            err += 1
            logging.error(str(e))
        else:
            count += 1
            if count % 10 == 0:
                await mesg.edit_text(f"Отправлено {count} сообщений из {len(users)}")
    await mesg.edit_text(f"Рассылка завершена\nОтправлено {count} из {len(users)}\nС ошибкой {err}", reply_markup=kb.back_admin)
    await state.clear()


@admin.callback_query(F.data == "config_mailings")
async def conf_mail(call: CallbackQuery, state: FSMContext, msg: Message, session: Session):
    await msg.edit_text("Выберите действие:", reply_markup=kb.conf_mails)


@admin.callback_query(F.data == "conf_admins")
async def conf_admins(call: CallbackQuery, state: FSMContext, msg: Message, session: Session):
    await msg.edit_text("Выберите действие", reply_markup=kb.admins_kb)


@admin.callback_query(F.data == "add_admin")
async def add_admin_handler(clbck: CallbackQuery, state: FSMContext, msg: Message):
    await msg.edit_text("Введите ID пользователя, которого хотите назначить админом", reply_markup=kb.back_admin)
    await state.set_state(AddAdmin.id)


@admin.message(AddAdmin.id)
async def add_adddmin(msg: Message, state: FSMContext, session: Session):
    try:
        chat_id = int(msg.text)
        user = await session.get(User, chat_id)
        user.is_admin = True
        await session.commit()
        await msg.answer("✅ Пользователь назначен админом", reply_markup=await kb.back("conf_admins"))
        await state.clear()
    except Exception as e:
        logging.error(e)
        await msg.answer("Произошла ошибка", reply_markup=kb.back_admin)


@admin.callback_query(F.data == "del_admin")
async def del_addddmin(clbck: CallbackQuery, state: FSMContext, msg: Message, session: Session, bot):
    await msg.edit_text("Выберите админа которого хотите удалить", reply_markup=await kb.del_admins_kb(session, bot))


@admin.callback_query(DelAdmin.filter(F.id))
async def del_addddmin(clbck: CallbackQuery, state: FSMContext, msg: Message, callback_data: DelAdmin, session: Session):
    user = await session.get(User, callback_data.id)
    user.is_admin = False
    await session.commit()
    await msg.edit_text("✅ Админ удалён", reply_markup=await kb.back("conf_admins"))


@admin.callback_query(LoadList.filter(F.file))
async def add_file(call: CallbackQuery, msg: Message, state: FSMContext, session: Session, callback_data: LoadList):
    await state.set_state(File.file)
    await state.update_data(file=LoadList.file)
    await msg.answer("Отправь мне TXT файл с одним значением на каждой строке, если значение уже есть в базе, оно будет пропущено", reply_markup=kb.back_admin)


@admin.message(F.document, File.file)
async def file_add(msg: Message, state: FSMContext, session: Session, bot: Bot):
    file_name = msg.document.file_name
    file_id = msg.document.file_id
    file_ext = file_name.split(".")[-1]
    if file_ext == "txt":
        f = await bot.download(file_id)
        lines = f.readlines()
        f.close()
        type = (await state.get_data()).get("file")
        if type == Load.STOP_WORDS:
            for i in lines:
                pass
    else:
        await msg.answer("Файл должен быть в формате TXT", reply_markup=kb.back_admin)
