from sqladmin import ModelView

from models import Phrase


class PhraseView(ModelView, model=Phrase):
    column_list = [Phrase.phrase]
    phrase = "Шаблон"
    phrase_plural = "Шаблоны"
    icon = ""
    column_details_list = [Phrase.id, Phrase.phrase]
    column_labels = {
        Phrase.id: "ID",
        Phrase.phrase: "Шаблон"
    }
