from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from filters.is_authenticated import IsAuthenticatedFilter
from db.models.faqs import Faq
from utils.logging import logger

router = Router()
router.message.filter(IsAuthenticatedFilter())

class AddFaqState(StatesGroup):
    waiting_for_text = State()
    waiting_for_short_description = State()
    waiting_for_document = State()

class EditFaqState(StatesGroup):
    waiting_for_short_description = State()
    waiting_for_description = State()
    waiting_for_file = State()

@router.message(F.text == "Часто задаваемые вопросы")
async def send_faq_via_button(message: types.Message, session: AsyncSession):
    await send_faq(message, session)

@router.message(Command("faq"))
async def send_faq(message: types.Message, session: AsyncSession):
    logger.info(f"User {message.from_user.id} called /faq")
    result = await session.execute(select(Faq))
    faqs = result.scalars().all()

    keyboard_builder = InlineKeyboardBuilder()
    for faq in faqs:
        keyboard_builder.add(
            InlineKeyboardButton(text=faq.short_description, callback_data=f'faq_{faq.id}')
        )

    keyboard_builder.row(
        InlineKeyboardButton(text='Добавить вопрос', callback_data='add_faq')
    )

    keyboard = keyboard_builder.as_markup()
    await message.reply("Выберите вопрос:", reply_markup=keyboard)
    logger.info(f"Sent FAQ keyboard to user {message.from_user.id}")

@router.callback_query(F.data == 'add_faq')
async def add_faq_callback(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"User {callback_query.from_user.id} started adding a new FAQ")
    await callback_query.message.reply("Пожалуйста, введите текст для нового FAQ:")
    await state.set_state(AddFaqState.waiting_for_text)
    await callback_query.answer()

@router.message(AddFaqState.waiting_for_text)
async def process_faq_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.reply("Теперь введите короткое описание для FAQ:")
    await state.set_state(AddFaqState.waiting_for_short_description)

@router.message(AddFaqState.waiting_for_short_description)
async def process_short_description(message: types.Message, state: FSMContext):
    await state.update_data(short_description=message.text)
    await message.reply("Пожалуйста, отправьте документ для FAQ, если он есть. Если документа нет, отправьте /skip.")
    await state.set_state(AddFaqState.waiting_for_document)

@router.message(AddFaqState.waiting_for_document, F.text == '/skip')
async def skip_document(message: types.Message, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    new_faq = Faq(
        text=user_data['text'],
        short_description=user_data['short_description'],
        document=None,
        display_in_keyboard=True
    )
    session.add(new_faq)
    await session.commit()
    await message.reply("Новый FAQ добавлен.")
    await state.clear()

@router.message(AddFaqState.waiting_for_document, F.document)
async def process_document(message: types.Message, state: FSMContext, session: AsyncSession):
    logger.debug("Добавление файлов")

    document = message.document
    file_id = document.file_id

    user_data = await state.get_data()
    new_faq = Faq(
        text=user_data['text'],
        short_description=user_data['short_description'],
        document=file_id,
        display_in_keyboard=True
    )
    session.add(new_faq)
    await session.commit()
    await message.reply("Новый FAQ добавлен.")
    await state.clear()

@router.callback_query(F.data.startswith('faq_'))
async def faq_callback(callback_query: types.CallbackQuery, session: AsyncSession,is_admin:bool):
    faq_id = int(callback_query.data.split('_')[1])
    logger.info(f"User {callback_query.from_user.id} clicked FAQ button with id {faq_id}")
    
    result = await session.execute(select(Faq).filter(Faq.id == faq_id))
    faq = result.scalar()

    if not faq:
        logger.warning(f"FAQ with id {faq_id} not found for user {callback_query.from_user.id}")
        await callback_query.message.reply("FAQ не найден.")
        return

    # Создание inline-клавиатуры
    keyboard = InlineKeyboardBuilder()
    if is_admin:
        keyboard.row(InlineKeyboardButton(text="Изменить короткое описание", callback_data=f"edit_short_desc_{faq_id}"))
        keyboard.row(InlineKeyboardButton(text="Изменить описание", callback_data=f"edit_desc_{faq_id}"))
        keyboard.row(InlineKeyboardButton(text="Изменить файл", callback_data=f"edit_file_{faq_id}"))

    keyboard = keyboard.as_markup()
    if faq.document:
        await callback_query.message.answer_document(faq.document, caption=faq.text, reply_markup=keyboard)
        logger.info(f"Sent document {faq.document} to user {callback_query.from_user.id}")
    else:
        await callback_query.message.answer(faq.text, reply_markup=keyboard)
        logger.info(f"Sent text FAQ to user {callback_query.from_user.id}")

    await callback_query.answer()

@router.callback_query(F.data.startswith('edit_short_desc_'))
async def edit_short_desc_callback(callback_query: types.CallbackQuery, state: FSMContext):
    faq_id = int(callback_query.data.split('_')[-1])
    await state.update_data(faq_id=faq_id)
    await callback_query.message.answer("Отправьте новое короткое описание.")
    await state.set_state(EditFaqState.waiting_for_short_description)

@router.message(EditFaqState.waiting_for_short_description)
async def process_new_short_description(message: types.Message, state: FSMContext, session: AsyncSession):
    new_short_description = message.text
    user_data = await state.get_data()
    faq_id = user_data['faq_id']

    result = await session.execute(select(Faq).filter(Faq.id == faq_id))
    faq = result.scalar()

    if faq:
        faq.short_description = new_short_description
        await session.commit()
        await message.reply("Короткое описание обновлено.")
        logger.info(f"Short description for FAQ {faq_id} updated by user {message.from_user.id}")

    await state.clear()

@router.callback_query(F.data.startswith('edit_desc_'))
async def edit_desc_callback(callback_query: types.CallbackQuery, state: FSMContext):
    faq_id = int(callback_query.data.split('_')[-1])
    await state.update_data(faq_id=faq_id)
    await callback_query.message.answer("Отправьте новое описание.")
    await state.set_state(EditFaqState.waiting_for_description)

@router.message(EditFaqState.waiting_for_description)
async def process_new_description(message: types.Message, state: FSMContext, session: AsyncSession):
    new_description = message.text
    user_data = await state.get_data()
    faq_id = user_data['faq_id']

    result = await session.execute(select(Faq).filter(Faq.id == faq_id))
    faq = result.scalar()

    if faq:
        faq.text = new_description
        await session.commit()
        await message.reply("Описание обновлено.")
        logger.info(f"Description for FAQ {faq_id} updated by user {message.from_user.id}")

    await state.clear()

@router.callback_query(F.data.startswith('edit_file_'))
async def edit_file_callback(callback_query: types.CallbackQuery, state: FSMContext):
    faq_id = int(callback_query.data.split('_')[-1])
    await state.update_data(faq_id=faq_id)
    await callback_query.message.answer("Отправьте новый файл.")
    await state.set_state(EditFaqState.waiting_for_file)

@router.message(EditFaqState.waiting_for_file, F.document)
async def process_new_file(message: types.Message, state: FSMContext, session: AsyncSession):
    logger.debug("Изменение файлов")

    document = message.document
    file_id = document.file_id
    user_data = await state.get_data()
    faq_id = user_data['faq_id']

    result = await session.execute(select(Faq).filter(Faq.id == faq_id))
    faq = result.scalar()
    logger.debug(faq)
    if faq:
        faq.document = file_id
        await session.commit()
        await message.reply("Файл обновлен.")
        logger.info(f"File for FAQ {faq_id} updated by user {message.from_user.id}")

    await state.clear()
