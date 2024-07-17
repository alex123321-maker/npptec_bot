import io
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from keyboards.main_reply import get_main_kb
from filters.is_admin import IsAdminFilter
from utils.logging import logger
from sqlalchemy import select
from db.models.users import Statuses, Users
from utils.config import settings

from keyboards.accept_or_reject_user_kb import get_admin_actions_kb

router = Router()


@logger.catch()
@router.message(CommandStart())
async def send_welcome(message: types.Message, session):
    user_id = message.from_user.id
    user_result  = await session.execute(select(Users).filter_by(user_id=user_id))
    user = user_result.scalar_one_or_none()
    logger.debug(f'Start: {user}')

    if not user:
        user = Users(user_id=user_id)
        session.add(user)
        
        try:
            for admin in settings.ADMIN_IDS:
                await message.bot.send_message(chat_id=admin, 
                                               text=f"Поступил запрос от пользователя:\nID: {message.from_user.id}\nИмя: {message.from_user.first_name}\nФамилия: {message.from_user.last_name or 'Не указано'}\n{message.from_user.mention_markdown()}",
                                               reply_markup=get_admin_actions_kb(user.user_id),
                                               parse_mode="Markdown")
                await session.commit()
        except Exception as e:
            logger.error(f'Ошибка при отправке запроса админу:{e}')
        await message.reply("Привет! Этот бот используется в корпоративных целях поэтому доступ к нему имеют только сотрудники. Мы отправили ваш запрос администратору.")

    elif user.status == Statuses.active:
        await message.reply("Привет, у вас есть доступ к боту.", reply_markup=get_main_kb())
    elif user.status == Statuses.not_authorized:
        await message.reply("Привет, ваша заявка всё ещё на рассмотрении.")
    elif user.status == Statuses.active:    
        await message.reply("Привет, для вас доступ к боту ограничен.")







