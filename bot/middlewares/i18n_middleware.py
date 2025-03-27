import logging
from typing import Any, Dict, Optional

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, TelegramObject
from aiogram.utils.i18n.middleware import FSMI18nMiddleware
from database import user_db

logger = logging.getLogger(__name__)


class LanguageMiddleware(FSMI18nMiddleware):
    def __init__(self, i18n):
        super().__init__(i18n)
    
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        if not isinstance(event, Message):
            return self.i18n.default_locale  
        
        fsm_context: Optional[FSMContext] = data.get("state")
        locale = None
        user_id = event.from_user.id

        if fsm_context:
            fsm_data = await fsm_context.get_data()
            locale = fsm_data.get(self.key, None)
            logger.debug(f"Locale from FSM: {locale}")

        if not locale:
            locale = await self.get_user_language_from_db(user_id=user_id)

            if fsm_context:
                await fsm_context.update_data(data={self.key: locale})
                logger.debug(f"Locale updated in FSM: {self.key=}, {locale=}")

            logger.debug(f"Locale from DB: {locale}")

        logger.debug(f"Locale: {locale}")
        return locale

    async def get_user_language_from_db(self, user_id: int) -> str:
        language = await user_db.get_user_language(user_id=user_id)
        return language
    