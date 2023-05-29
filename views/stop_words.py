from sqladmin import ModelView

from models import StopWord


class StopWordView(ModelView, model=StopWord):
    column_list = [StopWord.word]
    name = "Стоп-слово"
    name_plural = "Стоп-слова"
    icon = ""
    column_details_list = [StopWord.id, StopWord.word]
    column_labels = {
        StopWord.id: "ID",
        StopWord.word: "Стоп-слово"
    }
