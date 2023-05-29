from sqladmin import ModelView

from models import Answer


class AnswerView(ModelView, model=Answer):
    column_list = [Answer.user, Answer.question, Answer.answer]
    can_create = False
    can_edit = False
    can_delete = False
    name = "Вопрос"
    name_plural = "Вопросы"
    icon = ""
    column_details_list = [Answer.user, Answer.question, Answer.answer]
    column_labels = {
        Answer.user: "Пользователь",
        Answer.question: "Вопрос",
        Answer.answer: "Ответ"
    }
    column_export_exclude_list = [Answer.user]