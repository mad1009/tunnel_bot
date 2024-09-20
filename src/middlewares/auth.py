import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from config import ADMINS

logger = logging.getLogger(__name__)


class AuthorizationMiddleware(BaseMiddleware):
    """
    Helps to check if user is authorized to use the bot
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        print(user_id)
        if user_id in ADMINS:
            return await handler(event, data)
        else:
            logger.warning(f"Unautorized user sent message: {event.from_user.username}")
            await event.answer(
                "Service not availiable",
                show_alert=True
            )
