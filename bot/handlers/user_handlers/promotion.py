import re
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from database import promotion_db
from keyboards.user_kb import UserPromoCD, promotions_kb
from utils.user_check import check_user_premium_access


promotions_router = Router()


@promotions_router.message(F.text == "💲 1DOLLARSCLUB")
async def premium_club_handler(message: types.Message, state: FSMContext):
    """Handle Premium Club button - check subscription and show promotions"""
    if not await check_user_premium_access(message, state):
        return
    
    # If user has premium access, show promotions
    await list_promotions(message)


async def list_promotions(message: types.Message):
    """Show available promotions to premium users"""
    promotions = await promotion_db.get_active_promotions()

    if not promotions:
        return await message.answer(
            "💲 <b>1DOLLARSCLUB</b>\n\n"
            "⚠️ <b>Hozirda faol aksiyalar mavjud emas.</b>\n\n"
            "🕐 Yangi premium aksiyalar tez orada qo'shiladi. Kuzatib boring! 😉\n\n"
            "💎 <i>Siz 1DOLLARSCLUB a'zosisiz va yangi aksiyalar paydo bo'lishi bilan avtomatik xabar olasiz!</i>",
        )

    btn = await promotions_kb(promotions)
    text = (
        "💲 <b>1DOLLARSCLUB</b>\n\n"
        "🔥 <b>Siz uchun eksklyuziv aksiyalar:</b>\n\n"
        "📌 Istalgan aksiyani tanlang va maxsus promokodingizni oling!\n"
        "💰 Bu aksiyalar faqat 1DOLLARSCLUB a'zolari uchun mavjud!"
    )
    await message.answer(text, reply_markup=btn)



@promotions_router.message(F.text == "💥 Aksiyalar")
async def list_promotions(message: types.Message):
    promotions = await promotion_db.get_active_promotions()

    if not promotions:
        return await message.answer(
            "⚠️ <b>Hozirda faol aksiyalar mavjud emas.</b>\n\n"
            "🕐 Yangi aksiyalar tez orada qo‘shiladi. Kuzatib boring! 😉",
        )

    btn = await promotions_kb(promotions)
    text = "🔥 <b>Siz uchun TOP aksiyalar:</b>\n\n"
    text += "📌 Istalgan aksiyani tanlang va maxsus promokodingizni oling!"
    await message.answer(text, reply_markup=btn)


@promotions_router.callback_query(UserPromoCD.filter())
async def show_promotion(callback: types.CallbackQuery, callback_data: UserPromoCD):
    """Foydalanuvchi tanlagan aksiya haqida ma’lumot berish va promokod yaratish"""
    promo_id = callback_data.promo_id
    promotion = await promotion_db.get_promotion(promo_id)

    if not promotion:
        return await callback.answer(
            "❌ <b>Aksiya topilmadi!</b>\n\n" "Iltimos, boshqa aksiyani tanlang.",
            show_alert=True,
        )

    user_id = str(callback.from_user.id)
    promo_code = await promotion_db.generate_user_promo_code(user_id, promo_id)
    description_raw = promotion["description"]
    description = re.sub(r"<br\s*/?>", "\n", description_raw)


    if promo_code:
        text = (
            f"<b>{promotion['name']}</b>\n\n"
            f"{description}\n\n"
            f"🎟 <b>Sizning maxsus promo kodingiz:</b> <code>{promo_code}</code>\n\n"
            f"🔑 <i>⚠️ Ushbu promokod faqat 1 marta ishlatilishi mumkin!</i>\n"
            f"📅 <i>Promokodni muddati tugashidan oldin ishlating.</i>"
        )
    else:
        text = (
            f"🎉 <b>{promotion['name']}</b>\n\n"
            f"📄 {description}\n\n"
            f"✅ <b>Siz ushbu aksiya bo‘yicha promokoddan allaqachon foydalangansiz.</b>\n\n"
            f"ℹ️ Agar boshqa aksiyalarni ko‘rishni istasangiz, <b>💥 Aksiyalar</b> bo‘limiga o‘ting."
        )


    if promotion.get("image"):  
        image_file, image_data = await promotion_db.get_promotion_image(promotion["image"])

        if image_data and image_file:
            input_file = types.BufferedInputFile(image_data, filename=image_file["filename"])
            await callback.message.answer_photo(photo=input_file, caption=text)
            return await callback.answer()

    await callback.message.answer(text, disable_web_page_preview=True)
    await callback.answer()
