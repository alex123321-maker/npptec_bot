from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from middlewares.db import DbSessionMiddleware
from utils.config import settings
from utils.logging import logger

from sqlalchemy import select
from db.models.users import Statuses, Users

class IsAuthenticatedFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        session: AsyncSession = DbSessionMiddleware.session_context.get()
        user_id = message.from_user.id
        user_result = await session.execute(select(Users).filter_by(user_id=user_id))
        user = user_result.scalar_one_or_none()

        if user is None:
            return False

        # Проверяем и корректируем значение status, если оно не соответствует ожидаемому
        if user.status is None :
            if user.user_id in settings.ADMIN_IDS:
                user.status = Statuses.active
                await session.commit()
                logger.debug(f"User status: ADMIN, Authenticated: ADMIN")

                return True
            logger.debug(f"Меняю статус с None на {Statuses.not_authorized}")
            user.status = Statuses.not_authorized
            await session.commit()

      
        logger.debug(f"User status: {user.status}, Authenticated: {user.status != Statuses.not_authorized}")
        return user.status == Statuses.active