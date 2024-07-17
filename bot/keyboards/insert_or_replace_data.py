from enum import Enum
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

class Action(str, Enum):
    replace_data = "Заменить данные"
    insert = "Добавить к существующим"
    


class ReplaceOrInsertCD(CallbackData, prefix="roi"):
    action: Action



def replace_or_insert_kb():
    builder = InlineKeyboardBuilder()
    for action in Action:
        builder.button(
            text=action.value,
            callback_data=ReplaceOrInsertCD(action=action),
        )
    builder.adjust(2)
    return builder.as_markup()