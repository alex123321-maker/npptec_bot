import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from utils.logging import logger



from ..models.users import Employee, Department
import io

async def generate_excel_file(session: AsyncSession) -> io.BytesIO:
    logger.debug("Начало генерации Excel файла с информацией о сотрудниках")
    try:
        # Запрос данных из базы данных
        stmt = select(Employee).options(joinedload(Employee.department))
        result = await session.execute(stmt)
        employees = result.scalars().all()

        # Подготовка данных для Excel файла
        data = []
        for emp in employees:
            data.append({
                'Name': emp.name,
                'Email': emp.email,
                'Office Number': emp.office_number,
                'Office Phone': emp.office_phone,
                'Department': emp.department.name
            })

        df = pd.DataFrame(data)

        # Создание Excel файла в памяти
        excel_file = io.BytesIO()
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Employees')

        excel_file.seek(0)
        logger.debug("Excel файл успешно создан")
        return excel_file
    except Exception as e:
        logger.error(f"Ошибка при генерации Excel файла: {e}")
        raise

