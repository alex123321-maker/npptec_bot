from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery, InlineQuery
from typing import Callable, Dict, Any, Awaitable

class RoleMiddleware(BaseMiddleware):
    def __init__(self, admin_ids: list[int]):
        self.admin_ids = admin_ids
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None
        if event.message:
            user_id = event.message.from_user.id
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
        elif event.inline_query:
            user_id = event.inline_query.from_user.id

        if user_id:
            data['is_admin'] = user_id in self.admin_ids
        else:
            data['is_admin'] = False  # для остальных случаев

        return await handler(event, data)