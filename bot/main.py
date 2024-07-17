import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from middlewares.role import RoleMiddleware
from ui_commands import set_ui_commands
from middlewares.db import DbSessionMiddleware
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
from utils.config import settings
from router import setup_routers
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from utils.logging import logger




@logger.catch()
async def main():
    logger.debug("Запуск бота")

    engine = create_async_engine(url=settings.DATABASE_URL, echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    default_bot_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)

    bot = Bot(token=settings.BOT_TOKEN, session=AiohttpSession(), default=default_bot_properties)
    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.update.outer_middleware(RoleMiddleware(settings.ADMIN_IDS))
    main_router = setup_routers()
    dp.include_router(main_router)

    await set_ui_commands(bot)


    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.debug("Бот остановлен вручную")
 