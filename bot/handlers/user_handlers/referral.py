from aiogram import Bot, F, Router, types
from aiogram.utils.deep_linking import create_start_link
from database import user_db
from keyboards.common_kb import main_menu_kb

referral_router = Router()


@referral_router.message(F.text == "🎯 Referral")
async def send_referral_link(message: types.Message, bot: Bot):
    user_id = str(message.from_user.id)
    referral_link = await create_start_link(bot, payload=user_id, encode=True)

    user_info = await user_db.user_update(user_id)

    if not user_info.get('is_sponsor'):
        return await message.answer(
            f"🚀 <b>Sizga maxsus taklif!</b>\n\n"
            f"🫂 <b>Do‘stlaringizga ushbu havolani ulashing:</b>\n\n"
            f"🔗 {referral_link}\n\n"
            f"🎁 Har 5 ta yangi foydalanuvchi uchun <b>1 oy bepul</b> foydalanish imkoniyatini qo‘lga kiriting!\n"
            f"✅ Ko‘proq do‘stlaringizni taklif qiling va botdan bepul foydalanish muddatini uzaytiring!",
            reply_markup=main_menu_kb,
        )
         
    
    text = (
        f"🎉 <b>Hamkorlik havolangiz tayyor!</b>\n\n"
        f"🔗 {referral_link}\n\n"
        f"🤑 Ushbu havolani tarqating va foyda toping!\n\n"
        f"💸 Sizning havolangiz orqali obuna bo‘lgan har bir foydalanuvchidan <b>30% daromad</b> olasiz.\n"
        f"📊 Statistikasini esa alohida kabinet orqali kuzatishingiz mumkin.\n\n"
        f"✨ Ko‘proq ulashing — ko‘proq toping!"
    )
    return await message.answer(text)
