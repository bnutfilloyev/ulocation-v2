# === 1. BOT (Aiogram 3 backend, Webhook) ===
# Fayl: bot.py

import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import logging
import os

API_TOKEN = "1889005675:AAGTQ1dJz90_ZkokdGHrLTXFEr6fLZmQ9HU"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://abc123.ngrok-free.app/webhook"

# Logging
logging.basicConfig(level=logging.INFO)

# Bot & Dispatcher
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# === HANDLERS ===

@router.message(F.text == "/start")
async def start_handler(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(
        text="📷 QR kodni skanerla",
        web_app=WebAppInfo(url="https://your-domain.com/qr.html")
    )
    await message.answer("QR skaner WebApp'ni oching:", reply_markup=kb.as_markup())

@router.message(F.web_app_data)
async def webapp_data_handler(message: types.Message):
    data = message.web_app_data.data
    # Hozircha shunchaki foydalanuvchiga ko'rsatamiz
    await message.answer(f"📦 QR koddan olingan ma'lumot: <code>{data}</code>")

# === WEBHOOK SERVER ===

async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()

async def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    await on_startup(bot)
    try:
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
        await site.start()
        print(f"🌐 Webhook running at: {WEBHOOK_URL}")
        while True:
            await asyncio.sleep(3600)  # serverni tirik ushlab turish
    finally:
        await on_shutdown(bot)

if __name__ == "__main__":
    asyncio.run(main())