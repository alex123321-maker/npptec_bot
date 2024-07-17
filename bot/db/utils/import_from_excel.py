import random
import string
import pandas as pd
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logging import logger
from sqlalchemy import text

from ..models.users import Employee, Department



        


        

async def import_data_from_excel(session, file_content, clear_existing):
    try:
        # Читаем данные из файла Excel
        df = pd.read_excel(file_content)
        df = df.astype(str)
        logger.debug(df.tail(5))

        df['Department'] = df['Department'].replace([pd.NA, 'nan', 'NaN'], '-')
        
        # Получение списка уникальных отделов
        departments = set(df['Department'])
        logger.debug(departments)

        # Очистка таблиц если требуется
        if clear_existing:
            await session.execute(text('TRUNCATE TABLE employees CASCADE'))
            await session.execute(text('TRUNCATE TABLE departments CASCADE'))
            await session.commit()

        # Добавление отделов в базу данных
        existing_departments = {dept.name: dept for dept in (await session.execute(select(Department))).scalars()}
        for dept_name in departments:
            if dept_name not in existing_departments:
                department = Department(name=dept_name)
                session.add(department)
                existing_departments[dept_name] = department

        await session.commit()

        # Добавление сотрудников в базу данных
        for index, row in df.iterrows():
            department = existing_departments[row['Department']]
            employee = Employee(
                name=row[0],
                email=row[1],
                office_number=row[2],
                office_phone=row[3],
                department_id=department.id
            )
            session.add(employee)

        await session.commit()

        return "Удачно"

    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Произошла ошибка при добавлении данных в базу данных: {e.__repr__()}")
        return f"Произошла ошибка при обработке файла: {e}"
    except Exception as e:
        await session.rollback()
        logger.error(f"Произошла ошибка при обработке файла: {e.__repr__()}")
        return f"Произошла ошибка при обработке файла: {e.__repr__()}"
