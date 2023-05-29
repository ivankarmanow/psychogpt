import asyncio
import datetime
import logging
from typing import Iterable, List, Optional, Union

import asyncpg as pg
from sqlalchemy import (BigInteger, Boolean, Column, Date, DateTime,
                        ForeignKey, Integer, String)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, relationship

import config

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    reg_date = Column(Date, default=datetime.date.today())
    name = Column(String(50))
    age = Column(Integer)
    gender = Column(String(2))
    is_admin = Column(Boolean, default=False)
    pay = Column(String(10), default="standart")
    pay_to = Column(DateTime)
    answers = relationship("Answer", back_populates="user")

    def __str__(self):
        return f"Пользователь {self.id}"


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"))
    question = Column(String)
    answer = Column(String)
    user = relationship("User", back_populates="answers")

    def __str__(self):
        return f"Вопрос от {self.id}"


class StartQuestion(Base):
    __tablename__ = "start_questions"

    id = Column(Integer, primary_key=True)
    question = Column(String)


class StopWord(Base):
    __tablename__ = "stop_words"

    id = Column(Integer, primary_key=True)
    word = Column(String)


class Name(Base):
    __tablename__ = "names"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Phrase(Base):
    __tablename__ = "phrases"

    id = Column(Integer, primary_key=True)
    phrase = Column(String)
