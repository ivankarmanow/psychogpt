from sqladmin import ModelView

from models import User


def status_formatter(status: str) -> str:
    states = {
        "standart": "Стандартный",
        "premium": "Премиум",
        "trial": "Пробный"
    }
    return states.get(status, "Ограниченный")

class UserView(ModelView, model=User):
    column_exclude_list = [User.id, User.answers]
    column_formatters = {
        User.gender: lambda g: "Мужской" if g == 1 else "Женский",
        User.pay: status_formatter
    }
    can_create = False
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = ""
    column_details_list = [User.id, User.reg_date, User.name, User.age, User.gender, User.is_admin, User.pay, User.pay_to, User.answers]
    column_labels = {
        User.id: "Telegram ID", 
        User.reg_date: "Дата регистрации", 
        User.name: "Имя", 
        User.age: "Возраст", 
        User.gender: "Пол", 
        User.is_admin: "Админ", 
        User.pay: "Статус", 
        User.pay_to: "Статуст до"
    }
    column_formatters_detail = {
        User.gender: lambda g: "Мужской" if g == 1 else "Женский",
        User.pay: status_formatter
    }
    column_export_exclude_list = [User.answers]
    form_columns = [User.name, User.age, User.gender, User.is_admin, User.pay, User.pay_to]