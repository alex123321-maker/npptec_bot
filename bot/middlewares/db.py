

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from contextvars import ContextVar
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from utils.logging import logger


class DbSessionMiddleware(BaseMiddleware):
    session_context: ContextVar[AsyncSession] = ContextVar("session_context")

    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(self, handler, event, data):
        async with self.session_pool() as session:
            token = self.session_context.set(session)
            try:
                data['session'] = session  # Добавляем сессию в data
                return await handler(event, data)
            finally:
                self.session_context.reset(token)