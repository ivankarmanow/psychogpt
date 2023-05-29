from sqladmin import ModelView

from models import Name


class NameView(ModelView, model=Name):
    column_list = [Name.name]
    name = "Психолог"
    name_plural = "Психологи"
    icon = ""
    column_details_list = [Name.id, Name.name]
    column_labels = {
        Name.id: "ID",
        Name.name: "Психолог"
    }
