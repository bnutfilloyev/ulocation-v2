import logging
from typing import Any, Dict, Optional
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, TelegramObject
from aiogram.utils.i18n.middleware import FSMI18nMiddleware
from database import user_db

logger = logging.getLogger(__name__)

# Optional in-memory cache to reduce DB calls
_user_language_cache = {}

class LanguageMiddleware(FSMI18nMiddleware):
    def __init__(self, i18n):
        super().__init__(i18n)
    
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        # Default to system default locale for non-message events
        if not isinstance(event, Message):
            return self.i18n.default_locale
        
        user_id = event.from_user.id
        fsm_context: Optional[FSMContext] = data.get("state")
        locale = None
        
        # Try to get locale from FSM first
        if fsm_context:
            fsm_data = await fsm_context.get_data()
            locale = fsm_data.get(self.key)
            logger.debug(f"Locale from FSM: {locale}")

        # If not in FSM, try cache next
        if not locale and user_id in _user_language_cache:
            locale = _user_language_cache[user_id]
            logger.debug(f"Locale from cache: {locale}")
            
            # Update FSM if available
            if fsm_context:
                await fsm_context.update_data({self.key: locale})

        # If not in cache, try database
        if not locale:
            try:
                locale = await self.get_user_language_from_db(user_id)
                
                # Cache the result
                if locale:
                    _user_language_cache[user_id] = locale
                
                # Update FSM if available
                if fsm_context:
                    await fsm_context.update_data({self.key: locale})
                    logger.debug(f"Locale updated in FSM: {self.key=}, {locale=}")
                
                logger.debug(f"Locale from DB: {locale}")
            except Exception as e:
                logger.error(f"Error getting locale from DB: {e}")

        # Fallback to default locale if still not found
        if not locale:
            locale = self.i18n.default_locale
            logger.debug(f"Using default locale: {locale}")

        return locale

    async def get_user_language_from_db(self, user_id: int) -> str:
        try:
            language = await user_db.get_user_language(user_id=user_id)
            return language or self.i18n.default_locale
        except Exception as e:
            logger.error(f"Failed to get language from DB for user {user_id}: {e}")
            return self.i18n.default_locale