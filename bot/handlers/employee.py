import io
import textwrap
from uuid import uuid4
from aiogram import Router,types,F
from aiogram.filters import CommandStart, Command
from sqlalchemy import select,cast, String, update

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from filters.is_admin import IsAdminFilter
from keyboards.emp_actions import EmpAction, EmpActionsCD, EmpChangeCD, EmpFields, get_change_kb, get_departments_kb, get_employee_actions_kb
from db.utils.export_to_excel import generate_excel_file
from db.utils.import_from_excel import import_data_from_excel
from utils.logging import logger
from keyboards.insert_or_replace_data import Action, ReplaceOrInsertCD, replace_or_insert_kb
from keyboards.emp_paginator import *
from filters.is_authenticated import IsAuthenticatedFilter

from db.models.users import Department, Employee

router = Router()

router.message.filter(IsAuthenticatedFilter())


def format_employees_as_table(employees, page=1, obj_count=15):

    logger.debug(f'Выдана страница номер {page} по {obj_count} объектов ')

    def wrap_text(text, width):
        return textwrap.fill(text, width)

    header = f"{'Имя':<35} {'Email':<30} {'Офисный номер':<15} {'Телефон':<10} {'Отдел':<20}\n"
    table = header + "-" * len(header) + "\n"
    l_cursor = obj_count * (page - 1)
    r_cursor = l_cursor + obj_count

    for employee in employees[l_cursor:r_cursor]:
        name = wrap_text(employee.name, 35).split('\n')
        email = wrap_text(employee.email, 30).split('\n')
        office_number = wrap_text(employee.office_number, 15).split('\n')
        office_phone = wrap_text(employee.office_phone, 10).split('\n')
        department = wrap_text(employee.department.name, 20).split('\n')
        
        max_lines = max(len(name), len(email), len(office_number), len(office_phone), len(department))
        
        for i in range(max_lines):
            name_line = name[i] if i < len(name) else ''
            email_line = email[i] if i < len(email) else ''
            office_number_line = office_number[i] if i < len(office_number) else ''
            office_phone_line = office_phone[i] if i < len(office_phone) else ''
            department_line = department[i] if i < len(department) else ''
            
            table += f"{name_line:<35} {email_line:<30} {office_number_line:<15} {office_phone_line:<10} {department_line:<15}\n"
    
    return f"```\n{table}\n```"

def format_employee_as_string(employee):
    return (f"ID: {employee.id}\n"
            f"ФИО: {employee.name}\n"
            f"Email: {employee.email}\n"
            f"Кабинет: {employee.office_number}\n"
            f"Рабочий телефон: {employee.office_phone}\n"
            f"Отдел: {employee.department.name}\n")

@router.message(F.text == "Найти сотрудника")
async def find_employee_via_button(message: types.Message, session: AsyncSession):
    await find_employee(message, session)


@router.message(Command("find_employee"))
async def find_employee(message: types.Message, session: AsyncSession):
    keyboard = InlineKeyboardMarkup(inline_keyboard =[[InlineKeyboardButton(text="Найти сотрудника", switch_inline_query_current_chat="")]]
    )
    await message.reply(
        text="Чтобы найти сотрудника, нажмите на кнопку и введите запрос, по которому нужно произвести поиск",
        reply_markup=keyboard
    )

@router.message(Command("get_employee"))
async def show_employee(message: types.Message, session: AsyncSession, callback_query: types.CallbackQuery = None, p: int = 1, obj_c: int = 15):


    res = message.text.split()
    try:
        page = int(res[1])
    except Exception:
        page = p
    try:
        obj_count = int(res[2])
    except Exception:
        obj_count = obj_c

    stmt = select(Employee).options(joinedload(Employee.department))
    result = await session.execute(stmt)
    employees = result.scalars().all()

    if not employees:
        await message.reply("Нет данных о сотрудниках.")
        return
    
    total_pages = (len(employees) + obj_count - 1) // obj_count
    response = format_employees_as_table(employees, page=page, obj_count=obj_count)
    keyboard = generate_pagination_kb(current_page=page, total_pages=total_pages, obj_count=obj_count)
    
    if callback_query:
        await callback_query.message.edit_text(response, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await message.reply(response, parse_mode="Markdown", reply_markup=keyboard)

@router.callback_query(PageNavigationCD.filter())
async def paginate_employees(callback_query: types.CallbackQuery, callback_data: PageNavigationCD, session: AsyncSession,is_admin:bool):
    await show_employee(callback_query.message, session, callback_query, p=callback_data.page, obj_c=callback_data.obj_count)

@router.inline_query()
async def inline_employee_search(inline_query: InlineQuery, session: AsyncSession,is_admin:bool):
    if inline_query.chat_type != 'sender':
        return
    

    query_text = inline_query.query
    if not query_text:
        return

    offset = int(inline_query.offset) if inline_query.offset else 0
    limit = 49

    stmt = select(Employee).options(joinedload(Employee.department)).where(
        (Employee.name.ilike(f'%{query_text}%')) | 
        (Employee.email.ilike(f'%{query_text}%')) |
        (Employee.office_number.ilike(f'%{query_text}%')) |
        (Employee.office_phone.ilike(f'%{query_text}%')) |
        cast(Employee.id, String).ilike(f'%{query_text}%')
    ).offset(offset).limit(limit)
    result = await session.execute(stmt)
    employees = result.scalars().all()
    
    if not employees:
        await inline_query.answer(
            results=[],
            cache_time=1,
            switch_pm_text="Нет данных о сотрудниках.",
            switch_pm_parameter="inline_search_empty"
        )
        return
    
    articles = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=employee.name,
            input_message_content=InputTextMessageContent(message_text=format_employee_as_string(employee)),
            description=f"Email: {employee.email}, Office: {employee.office_number}",
            reply_markup=get_employee_actions_kb(emp_id=employee.id,is_admin=is_admin)
        )
        for employee in employees
    ]
    logger.debug(f"Количество результатов: {len(articles)}")

    next_offset = str(offset + limit) if len(employees) == limit else None

    try:
        if len(articles) > 50:
            articles = articles[:50]
        await inline_query.answer(articles, cache_time=1,next_offset=next_offset)
    except Exception as e:
        logger.error(e)


@router.callback_query(EmpActionsCD.filter(F.action == EmpAction.change))
async def handle_change(callback: types.CallbackQuery, callback_data: EmpActionsCD, session):

    emp_id = callback_data.id
    new_kb = get_change_kb(emp_id)
    
    await callback.bot.edit_message_reply_markup(
            inline_message_id=callback.inline_message_id,
            reply_markup=new_kb
        )
    await callback.answer()


class EmployeeForm(StatesGroup):
    waiting_for_new_value = State()
    waiting_for_department_selection = State()

@logger.catch()
@router.callback_query(EmpChangeCD.filter())
async def handle_change_field(callback: types.CallbackQuery, callback_data: EmpChangeCD, state: FSMContext, session: AsyncSession,is_admin:bool):
    emp_id = callback_data.id
    field_to_change = callback_data.field

    if field_to_change == EmpFields.department:
        logger.debug(f"Запрос выбора нового отдела для сотрудника с ID {emp_id}")


        stmt = select(Department)
        result = await session.execute(stmt)
        departments = result.scalars().all()


        department_kb = await get_departments_kb(departments,is_admin)
        
       
        
        await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text="Выберите новый отдел:",
            reply_markup=department_kb
        )

        await state.update_data(emp_id=emp_id, field=field_to_change)
        await state.set_state(EmployeeForm.waiting_for_department_selection)
        await callback.answer()
        return

    logger.debug(f"Запрос нового значения для поля {field_to_change} у пользователя для сотрудника с ID {emp_id}")

    if callback.message:
        await callback.message.edit_text(f"Введите новое значение для поля {field_to_change.value}:")
    elif callback.inline_message_id:
        await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=f"Введите новое значение для поля {field_to_change.value}:"
        )

    await state.update_data(emp_id=emp_id, field=field_to_change)
    await state.set_state(EmployeeForm.waiting_for_new_value)
    await callback.answer()

@router.callback_query(F.data.startswith("select_department"))
async def select_department(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    department_id = int(callback.data.split(":")[1])
    user_data = await state.get_data()
    emp_id = user_data["emp_id"]

    try:
        stmt = update(Employee).where(Employee.id == emp_id).values({"department_id": department_id})
        await session.execute(stmt)
        await session.commit()

        await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=f"Отдел успешно обновлен."
        )
        logger.info(f"Отдел успешно обновлен для сотрудника с ID {emp_id}")
    except Exception as e:
        logger.error(f"Ошибка при изменении отдела для сотрудника с ID {emp_id}: {e}")
        await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=f"Произошла ошибка при обновлении отдела."
        )
       

    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "add_department")
async def add_department(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.send_message(chat_id=callback.message.chat.id,text="Введите название нового отдела:")
    await state.set_state(EmployeeForm.waiting_for_new_value)
    await state.update_data(add_new_department=True)
    await callback.answer()

@router.message(EmployeeForm.waiting_for_new_value)
async def receive_new_value(message: types.Message, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    
    if user_data.get("add_new_department"):
        department_name = message.text
        new_department = Department(name=department_name)
        session.add(new_department)
        await session.commit()

        await message.answer(f"Новый отдел '{department_name}' успешно добавлен.")
        await state.clear()
        return

    emp_id = user_data["emp_id"]
    field_to_change = user_data["field"]
    new_value = message.text

    logger.debug(f"Получено новое значение для поля {field_to_change} сотрудника с ID {emp_id}: {new_value}")

    column_name = field_to_change.name

    try:
        stmt = update(Employee).where(Employee.id == emp_id).values({column_name: new_value})
        await session.execute(stmt)
        await session.commit()

        await message.answer(f"Поле {field_to_change.value} успешно обновлено на {new_value}")
        logger.info(f"Поле {field_to_change.value} успешно обновлено на {new_value} для сотрудника с ID {emp_id}")
    except Exception as e:
        logger.error(f"Ошибка при изменении поля {field_to_change} для сотрудника с ID {emp_id}: {e}")
        await message.answer(f"Произошла ошибка при обновлении поля {field_to_change.value}")

    await state.clear()