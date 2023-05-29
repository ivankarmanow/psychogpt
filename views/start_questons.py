from sqladmin import ModelView

from models import StartQuestion


class StartQuestView(ModelView, model=StartQuestion):
    column_list = [StartQuestion.question]
    name = "Стартовый вопрос"
    name_plural = "Стартовые вопросы"
    icon = ""
    column_details_list = [StartQuestion.id, StartQuestion.question]
    column_labels = {
        StartQuestion.id: "ID",
        StartQuestion.question: "Стартовый вопрос"
    }
