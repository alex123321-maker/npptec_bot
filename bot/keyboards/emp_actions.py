from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from enum import Enum
from aiogram import types

class EmpAction(str, Enum):
    change = "Изменить"
    delete = "Удалить"

class EmpActionsCD(CallbackData, prefix="emp_act"):
   id:int
   action:EmpAction 

def get_employee_actions_kb(emp_id:int,is_admin=False):

    builder = InlineKeyboardBuilder()

    builder.button(
        text=EmpAction.change.value,
        callback_data=EmpActionsCD(id = emp_id,action=EmpAction.change),
    )
    if is_admin:
        builder.button(
        text=EmpAction.delete.value,
        callback_data=EmpActionsCD(id = emp_id,action=EmpAction.delete),
    )
    builder.adjust(1)
    return builder.as_markup()


class EmpFields(str, Enum):
    name = "ФИО"
    email = "Email"
    office_number = "Кабинет"
    office_phone = "Телефон"
    department = "Отдел"




class EmpChangeCD(CallbackData, prefix="emp_chng"):
   id:int
   field:EmpFields


def get_change_kb(emp_id:int):

    builder = InlineKeyboardBuilder()


    for field in EmpFields:
        builder.button(
            text=field.value,
            callback_data=EmpChangeCD(id = emp_id,field=field),
        )
    builder.adjust(1,1,1,1,1)

    return builder.as_markup()

async def get_departments_kb(departments,is_admin) -> types.InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    for department in departments:
        builder.row(types.InlineKeyboardButton(
            text=department.name,
            callback_data=f"select_department:{department.id}"
        ),width=1)
    if is_admin:
        builder.row(types.InlineKeyboardButton(
            text="Добавить отдел",
            callback_data="add_department"
        ))

    
    return builder.as_markup()



