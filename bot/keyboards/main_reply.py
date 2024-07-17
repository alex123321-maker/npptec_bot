from enum import Enum
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_kb():
    builder  = ReplyKeyboardBuilder()

    builder.button(
        text="Найти сотрудника"
                   )
    builder.button(
        text="Часто задаваемые вопросы"
                   )
    return builder.as_markup()