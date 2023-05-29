import asyncio
import sqlite3
import uuid

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from starlette.requests import Request
from starlette.responses import RedirectResponse

import config
import models
from views import (AnswerView, NameView, PhraseView, StartQuestView,
                   StopWordView, UserView)

lite = sqlite3.connect("admin.db")


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        cur = lite.cursor()
        res = cur.execute("SELECT * FROM admins").fetchall()
        suc = False
        for i in res:
            if username == i[1] and password == i[2]:
                suc = True
                admin_id = i[0]
                break
        if suc:
            token = str(uuid.uuid4())
            cur.execute("INSERT INTO tokens VALUES (?, ?)", (admin_id, token))
            lite.commit()
            cur.close()
            request.session.update({"token": token})
            return True
        else:
            return False

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        token = request.session.get("token")
        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        cur = lite.cursor()
        tokens = cur.execute("SELECT token FROM tokens").fetchall()
        suc = False
        for i in tokens:
            if i[0] == token:
                suc = True
                break
        cur.close()
        return suc


authentication_backend = AdminAuth(secret_key="12345")


async def setup_db():
    engine = create_async_engine(url=config.DATABASE_URL, echo=True)
    # async with engine.begin() as conn:
    #     await conn.run_sync(db.Base.metadata.drop_all)
    #     await conn.run_sync(db.Base.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    return engine, sessionmaker

app = FastAPI()


@app.on_event("startup")
async def main():
    engine = (await setup_db())[0]
    admin = Admin(app, engine, base_url="/", title="Админ-панель бота",
                  authentication_backend=authentication_backend)
    admin.add_view(UserView)
    admin.add_view(AnswerView)
    admin.add_view(NameView)
    admin.add_view(PhraseView)
    admin.add_view(StopWordView)
    admin.add_view(StartQuestView)
