from loguru import logger
import sys
import logging
import textwrap

def configure_logging():
    logger.remove()  # Удаляем стандартный логгер
    logger.add(
        sys.stdout,
        format="<green><bold>[{time}]</bold></green> | <level><bold>{level:<5}</bold></level> | <yellow>{file:>25}</yellow>:<lr>{function:^25}</lr>:<b><yellow>{line:<5}</yellow></b> |<cyan>{message}</cyan>",
        level="TRACE"
    )
    logger.add("logs/debug.log", format="[{time}]   |   {level}   |   {message}", level="TRACE", rotation="1 MB", compression="zip")
    return logger

logger = configure_logging()

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Преобразуем уровень логирования в строку или целое число
        try:
            level = logger.level(record.levelname).name if logger.level(record.levelname, no=None) is not None else record.levelno
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def intercept_sqlalchemy_logs():
    logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.dialects').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.orm').setLevel(logging.INFO)
    
    intercept_handler = InterceptHandler()

    # Перехватываем все логгеры SQLAlchemy
    for name in logging.root.manager.loggerDict.keys():
        if name.startswith('sqlalchemy'):
            log = logging.getLogger(name)
            log.handlers = []  # Убираем все старые обработчики
            log.propagate = False  # Отключаем распространение логов
            log.addHandler(intercept_handler)

intercept_sqlalchemy_logs()
