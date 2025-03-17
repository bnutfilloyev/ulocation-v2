from aiogram import Router, types, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from keyboards.common_kb import  main_menu_kb, remove_kb
from structures.database import db
from aiogram.utils.deep_linking import decode_payload
from aiogram.utils.i18n import gettext as _

from utils.user_check import check_user_stepwise

start_router = Router()


@start_router.message(Command("start"))
async def start_command(
    message: types.Message, state: FSMContext, command: CommandObject, bot: Bot
):
    await db.user_update(user_id=message.from_user.id)

    if command.args:
        referrer_id = decode_payload(command.args)
        if not referrer_id:
            return await message.answer(
                "❌ <b>Uzr, bu havola noto‘g‘ri yoki muddati tugagan!</b>\n\n"
                "🔎 Iltimos, havolangizni tekshiring va qaytadan urinib ko‘ring."
            )
        
        if not await db.add_referral(user_id=message.from_user.id, referrer_id=referrer_id):
            return await message.answer(
                "❌ <b>Siz avval bu referral havola orqali tizimga qo‘shilgansiz</b> yoki "
                "<b>havola noto‘g‘ri!</b>\n\n"
                "🔄 Yangi referral havola bilan qayta urinib ko'ring."
            )
        
        await message.answer(
            "✅ <b>Tabriklaymiz!</b> Siz referral orqali tizimga muvaffaqiyatli qo‘shildingiz! 🎉\n\n"
            "💰<b>Do‘stlaringizni taklif qilib, bonuslarga ega bo‘lishni unutmang!</b>\n\n"
            "🎯 <b>Eslatma:</b> Bonuslaringiz siz botga obuna bo‘lgandan so‘ng avtomatik ravishda qo‘shiladi."
        )
        await bot.send_message(
            referrer_id,
            f"🎯 Sizning referral havolangiz orqali yangi foydalanuvchi qo‘shildi: <b>{message.from_user.full_name}</b>"
        )


    if not await check_user_stepwise(message, state):
        return
    

    text = (
        "😊 <b>Sizni yana ko‘rishdan xursandmiz!</b>\n\n"
        "📌 <b>Botdan foydalanish uchun quyidagi tugmalardan foydalaning:</b>"
    )
    await message.answer(text=_(text), reply_markup=main_menu_kb)


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
    await message.answer(
        text=text,
        reply_markup=remove_kb,
    )
    return await state.clear()
