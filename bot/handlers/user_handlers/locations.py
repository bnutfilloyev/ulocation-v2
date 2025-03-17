from aiogram import F, Router, types
from middlewares.subscription_middleware import SubscriptionMiddleware

locations_router = Router()


@locations_router.message(F.text == "📍 Lokatsiyalar")
async def list_locations(message: types.Message):
    await message.answer("Hali qo'shilgan lokatsiyalar yo'q.")
