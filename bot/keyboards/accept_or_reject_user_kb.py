from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardMarkup,InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from enum import Enum
from aiogram import types


class AdmAction(str, Enum):
    accept = "Принять"
    reject = "Отклонить"


class AdmActionsCD(CallbackData, prefix="adm_act"):
   id:int
   action:AdmAction


def get_admin_actions_kb(emp_id:int): 

    builder = InlineKeyboardBuilder()

    for action in AdmAction:
        builder.button(
            text=action.value,
            callback_data=AdmActionsCD(id = emp_id,action=action),
        )

    return builder.as_markup()

def create_user_keyboard(users):
    builder = InlineKeyboardBuilder()

    for u in users:
        builder.row(
            InlineKeyboardButton(
                text=f'Id: {u.user_id}, {AdmAction.accept.value}',
                callback_data=AdmActionsCD(id=u.user_id, action=AdmAction.accept).pack()
            ),
            InlineKeyboardButton(
                text=f'Id: {u.user_id}, {AdmAction.reject.value}',
                callback_data=AdmActionsCD(id=u.user_id, action=AdmAction.reject).pack()
            )
        )
    return builder.as_markup()