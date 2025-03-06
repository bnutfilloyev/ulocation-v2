from datetime import datetime
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from structures.database import db  
from keyboards.user_kb import UserPromoCD, promotions_kb

promotions_router = Router()

@promotions_router.message(F.text == "💥 Aksiyalar")
async def list_promotions(message: types.Message):
    """Foydalanuvchiga mavjud aksiyalarni chiqarish"""
    promotions = await db.get_active_promotions()
    
    if not promotions:
        return await message.answer(
            "⚠️ <b>Hozirda faol aksiyalar mavjud emas.</b>\n\n"
            "🕐 Yangi aksiyalar tez orada qo‘shiladi. Kuzatib boring! 😉",
            parse_mode="HTML"
        )

    btn = await promotions_kb(promotions)
    text = "🔥 <b>Siz uchun TOP aksiyalar:</b>\n\n"
    text += "📌 Istalgan aksiyani tanlang va maxsus promokodingizni oling!"
    await message.answer(text, reply_markup=btn, parse_mode="HTML")


@promotions_router.callback_query(UserPromoCD.filter())
async def show_promotion(callback: types.CallbackQuery, callback_data: UserPromoCD):
    """Foydalanuvchi tanlagan aksiya haqida ma’lumot berish va promokod yaratish"""
    promo_id = callback_data.promo_id
    promotion = await db.get_promotion(promo_id)

    if not promotion:
        return await callback.answer(
            "❌ <b>Aksiya topilmadi!</b>\n\n"
            "Iltimos, boshqa aksiyani tanlang.", show_alert=True, parse_mode="HTML"
        )

    user_id = str(callback.from_user.id)
    promo_code = await db.generate_user_promo_code(user_id, promo_id)

    text = (
        f"🎉 <b>{promotion['name']}</b>\n\n"
        f"📄 {promotion['description']}\n\n"
        f"🎟 <b>Sizning maxsus promo kodingiz:</b> <code>{promo_code}</code>\n\n"
        f"🔑 <i>⚠️ Ushbu promokod faqat 1 marta ishlatilishi mumkin!</i>\n"
        f"📅 <i>Promokodni muddati tugashidan oldin ishlating.</i>"
    )

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()