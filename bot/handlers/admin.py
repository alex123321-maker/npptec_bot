import io
from aiogram import Router,types,F
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,cast, String, update
from aiogram.filters import  Command
from bot.keyboards.main_reply import get_main_kb
from filters.document import NotAddFaqState
from handlers.faqs import AddFaqState
from filters.is_authenticated import IsAuthenticatedFilter
from db.utils.export_to_excel import generate_excel_file
from db.utils.import_from_excel import import_data_from_excel
from keyboards.insert_or_replace_data import Action, ReplaceOrInsertCD, replace_or_insert_kb
from filters.is_admin import IsAdminFilter

from keyboards.accept_or_reject_user_kb import AdmAction,AdmActionsCD, create_user_keyboard

from db.models.users import Statuses, Users


from utils.logging import logger

router = Router()
router.message.filter(IsAdminFilter(),IsAuthenticatedFilter())



@logger.catch()
@router.message(Command("get_users"))
async def get_users(message:types.Message, session: AsyncSession):
    try:
        # Выполнение запроса к базе данных
        result = await session.execute(select(Users))
        users = result.scalars().all()

        if users:
            # Формирование информации о пользователях
            users_info = "\n".join([f"ID: [{u.user_id}](tg://user?id={u.user_id})" for u in users])
            await message.reply(f"Пользователи в базе данных:\n\n{users_info}",parse_mode="Markdown")
        else:
            await message.reply("В базе данных нет зарегистрированных пользователей.")
    except Exception as ex:
        logger.error(f"Ошибка при получении пользователей: {ex}")



@router.callback_query(AdmActionsCD.filter())
async def handle_accept(callback: types.CallbackQuery, callback_data: AdmActionsCD, session:AsyncSession):
    user_id = callback_data.id
    user_result  = await session.execute(select(Users).filter_by(user_id=user_id))
    user = user_result.scalar_one_or_none()
    if callback_data.action == AdmAction.accept and user.status == Statuses.not_authorized:
        user.status = Statuses.active
        await callback.message.bot.send_message(
            chat_id=user_id,
            text="Запрос рассмотрен, теперь вам доступен функционал бота.",
            reply_markup=get_main_kb()
        )
        logger.debug(f"Запрос для пользователя с id:{user_id} принят")

        await session.commit()
        await callback.answer(text='Успешно')


    elif callback_data.action == AdmAction.reject and user.status == Statuses.not_authorized:
        user.status = Statuses.banned
        await callback.message.bot.send_message(
            chat_id=user_id,
            text="Запрос рассмотрен, доступ к боту ограничен."
        )
        logger.debug(f"Запрос для пользователя с id:{user_id} отклонён")
        await session.commit()
        await callback.answer(text='Успешно')

@logger.catch()
@router.message(NotAddFaqState(),F.document)
async def handle_docs(message: types.Message,session):
    logger.debug("Excel файл добавление")

    if not (message.document and message.document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
        return
    await message.reply("Вы хотите добавить эти данные к существуюшим или заменить все данные?", reply_markup=replace_or_insert_kb())

@logger.catch()
@router.message(Command('export_employee') )
async def handle_docs(message: types.Message, session: AsyncSession):
    logger.debug("Запрошен экспорт информации о сотрудниках")
    try:
        excel_file = await generate_excel_file(session)
        input_file = types.BufferedInputFile(excel_file.read(), filename='employees.xlsx')
        await message.bot.send_document(message.chat.id, input_file)
        logger.info(f"Файл с информацией о сотрудниках успешно отправлен в чат {message.chat.id}")
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса на экспорт информации о сотрудниках: {e}")

@logger.catch()
@router.message(Command('import_employee') )
async def import_employee(message: types.Message, session: AsyncSession):
    await message.bot.send_message(message.chat.id, 
                                   text="Для того чтобы импортировать сотрудников, вам необходимо отправить Excel (.xlsx) файл")
    
@logger.catch()
@router.message(Command('get_active_users') )
async def import_employee(message: types.Message, session: AsyncSession):

    try:
        # Выполнение запроса к базе данных
        result = await session.execute(select(Users).filter_by(status=Statuses.active))
        users = result.scalars().all()

        if users:
            # Формирование информации о пользователях
            users_info = "\n".join([f"ID: [{u.user_id}](tg://user?id={u.user_id})" for u in users])
            await message.reply(f"Активированные пользователи в базе данных:\n\n{users_info}",parse_mode="Markdown")
        else:
            await message.reply("В базе данных нет активированных пользователей.")
    except Exception as ex:
        logger.error(f"Ошибка при получении пользователей: {ex}")

@logger.catch()
@router.message(Command('get_not_authorized_users') )
async def import_employee(message: types.Message, session: AsyncSession):

    try:
        # Выполнение запроса к базе данных
        result = await session.execute(select(Users).filter_by(status=Statuses.not_authorized))
        users = result.scalars().all()

        if users:
            
            users_info = "\n".join([f"ID: [{u.user_id}](tg://user?id={u.user_id})" for u in users])
            await message.reply(f"Пользователи ожидающие ответов:\n\n{users_info}",parse_mode="Markdown" ,reply_markup=create_user_keyboard(users))
        else:
            await message.reply("В базе данных нет пользователей ожидающих доступ.")
    except Exception as ex:
        logger.error(f"Ошибка при получении пользователей: {ex}")

@logger.catch()
@router.message(Command('get_rejected_users') )
async def import_employee(message: types.Message, session: AsyncSession):

    try:
        # Выполнение запроса к базе данных
        result = await session.execute(select(Users).filter_by(status=Statuses.banned))
        users = result.scalars().all()

        if users:
            # Формирование информации о пользователях
            users_info = "\n".join([f"ID: [{u.user_id}](tg://user?id={u.user_id})" for u in users])
            await message.reply(f"Заблокированные пользователи:\n\n{users_info}",parse_mode="Markdown")
        else:
            await message.reply("В базе данных нет заблокированных пользлователей.")
    except Exception as ex:
        logger.error(f"Ошибка при получении пользователей: {ex}")

@logger.catch()
@router.callback_query(ReplaceOrInsertCD.filter(F.action == Action.replace_data) )
async def handle_replace(callback: types.CallbackQuery, callback_data: ReplaceOrInsertCD, session):
    message = callback.message.reply_to_message
    file_id =callback.message.reply_to_message.document.file_id
    try:
        file_info = await message.bot.get_file(file_id)
        logger.debug(f"Файл найден: {file_info}")
        file_data:io.BytesIO = await message.bot.download(file_info)

        logger.debug(f"Выбрана замена данных")
        result = await import_data_from_excel(session, file_data, True)


        await callback.message.edit_text(result,reply_markup=None)

        await callback.answer()


    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        await callback.message.reply("Произошла ошибка при обработке файла.")
        await callback.answer()

@logger.catch()
@router.callback_query(ReplaceOrInsertCD.filter(F.action == Action.insert) )
async def handle_insert(callback: types.CallbackQuery, callback_data: ReplaceOrInsertCD, session):
    message = callback.message.reply_to_message
    file_id =callback.message.reply_to_message.document.file_id
    try:
        file_info = await message.bot.get_file(file_id)
        logger.debug(f"Файл найден: {file_info}")
        file_data:io.BytesIO = await message.bot.download(file_info)

        logger.debug(f"Выбрана замена данных")
        result = await import_data_from_excel(session, file_data, False)


        await callback.message.edit_text(result,reply_markup=None)
        # await callback.answer()


    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        await callback.message.reply("Произошла ошибка при обработке файла.")
        await callback.answer()
