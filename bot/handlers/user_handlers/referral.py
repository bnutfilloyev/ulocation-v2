from aiogram import Bot, F, Router, types
from aiogram.utils.deep_linking import create_start_link

from keyboards.common_kb import main_menu_kb

referral_router = Router()


@referral_router.message(F.text == "🎯 Referral")
async def send_referral_link(message: types.Message, bot: Bot):
    user_id = str(message.from_user.id)
    referral_link = await create_start_link(bot, payload=user_id, encode=True)
    await message.answer(
        f"🚀 <b>Sizga maxsus taklif!</b>\n\n"
        f"🫂 <b>Do‘stlaringizga ushbu havolani ulashing:</b>\n\n"
        f"🔗 {referral_link}\n\n"
        f"🎁 Har 5 ta yangi foydalanuvchi uchun <b>1 oy bepul</b> foydalanish imkoniyatini qo‘lga kiriting!\n"
        f"✅ Ko‘proq do‘stlaringizni taklif qiling va botdan bepul foydalanish muddatini uzaytiring!",
        reply_markup=main_menu_kb,
    )
