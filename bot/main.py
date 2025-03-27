"""This file represent startup bot logic."""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.utils.i18n import I18n
from configuration import conf
from handlers import routers
from middlewares.i18n_middleware import LanguageMiddleware
from middlewares.subscription_middleware import SubscriptionMiddleware
from structures.schedule import on_startup

i18n = I18n(path='locales', default_locale='uz', domain='messages')

def get_dispatcher(
    storage: BaseStorage = MemoryStorage(),
    fsm_strategy: FSMStrategy | None = FSMStrategy.CHAT,
    event_isolation: BaseEventIsolation | None = None,
):
    """This function set up dispatcher with routers, filters and middlewares."""
    dp = Dispatcher(
        storage=storage,
        fsm_strategy=fsm_strategy,
        events_isolation=event_isolation,
    )

    dp.message.middleware(LanguageMiddleware(i18n))
    dp.message.middleware(SubscriptionMiddleware())

    for router in routers:
        dp.include_router(router)

    return dp


async def start_bot():
    """This function will start bot with polling mode."""
    bot = Bot(token=conf.bot.token, default=DefaultBotProperties(parse_mode="HTML"))
    await on_startup(bot)
    dp = get_dispatcher()

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(start_bot())
