from aiogram import Bot
from aiogram.types import BotCommandScopeChat, BotCommand,BotCommandScopeAllPrivateChats
from utils.config import settings


async def set_ui_commands(bot: Bot):
    """
    Sets bot commands in UI
    :param bot: Bot instance
    """
    commands = [
        BotCommand(command="start", description="Регистрация"),
        BotCommand(command="get_employee", description="Посмотерть сотрудников"),
        BotCommand(command="find_employee", description="Найти сотрудника"),
        BotCommand(command="faq", description="Часто задаваемые вопросы")


    ]
    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeAllPrivateChats()
    )
    admins_commands =commands + [
        BotCommand(command="get_users", description="Посмотреть всех пользователей бота"),
        BotCommand(command="get_active_users", description="Посмотреть всех активированных пользователей"),
        BotCommand(command="get_not_authorized_users", description="Посмотреть всех пользователей ожидающих доступ"),
        BotCommand(command="get_rejected_users", description="Посмотреть всех отклонённых пользователей"),
        BotCommand(command="import_employee", description="Отправьте excel файл для добавления информации о сотрудниках"),
        BotCommand(command="export_employee", description="Получить excel файл в котором хранится информация о сотрудниках"),
    ]

    for id in settings.ADMIN_IDS:
        await bot.set_my_commands(
            commands=admins_commands,
            scope=BotCommandScopeChat(chat_id=id)
     )


