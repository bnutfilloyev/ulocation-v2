from aiogram import Bot, Router, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from database import user_db
from keyboards.common_kb import main_menu_kb, remove_kb
from utils.user_check import check_user_referral, check_user_stepwise

start_router = Router()


@start_router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext, command: CommandObject, bot: Bot):
    await user_db.user_update(user_id=message.from_user.id)

    await check_user_referral(message, command, bot)
    if not await check_user_stepwise(message, state): return
    
    text = (
        "😊 <b>Sizni yana ko‘rishdan xursandmiz!</b>\n\n"
        "📌 <b>Botdan foydalanish uchun quyidagi tugmalardan foydalaning:</b>"
    )
    await message.answer(text=text, reply_markup=main_menu_kb)


@start_router.message(Command("help"))
async def help_command(message: types.Message, state: FSMContext):
    text = (
        "🆘 <b>Yordam bo‘limi</b>\n\n"
        "🔹 Agar botdan foydalanishda muammolarga duch kelsangiz yoki qo‘shimcha savollaringiz bo‘lsa, biz sizga yordam bera olamiz.\n\n"
        "💡 <b>Asosiy buyruqlar:</b>\n"
        "👉 <code>/start</code> - Botni qayta ishga tushirish\n"
        "👉 <code>/help</code> - Yordam olish\n"
        "❓ Qo‘shimcha savollaringiz bo‘lsa, administratorga murojaat qiling."
    )
    await message.answer(text=text, reply_markup=remove_kb)
    return await state.clear()
