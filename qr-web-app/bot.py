import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = "1889005675:AAGTQ1dJz90_ZkokdGHrLTXFEr6fLZmQ9HU"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(F.text == "/start")
async def start_handler(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(
        text="📷 QR kodni skanerla",
        web_app=WebAppInfo(url="https://66b2-198-163-205-69.ngrok-free.app/qr.html"),
    )
    await message.answer("QR skaner WebApp'ni oching:", reply_markup=kb.as_markup())

@dp.message()
async def webapp_data_handler(message: types.Message):
    data = message.web_app_data.data
    await message.answer(f"📦 QR koddan olingan ma'lumot: <code>{data}</code>")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
