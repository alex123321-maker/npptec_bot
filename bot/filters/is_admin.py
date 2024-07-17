from aiogram.filters import BaseFilter
from aiogram.types import Message
from utils.config import settings
from utils.logging import logger


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        logger.debug(f"IDS:{settings.ADMIN_IDS} My ID:{message.from_user.id}")
        return message.from_user.id in settings.ADMIN_IDS