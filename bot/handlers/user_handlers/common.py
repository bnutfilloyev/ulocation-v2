from aiogram import Router, types, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from configuration import conf
from keyboards.common_kb import contact_kb, main_menu_kb, remove_kb
from structures.database import db
from structures.states import RegState
from aiogram.utils.deep_linking import decode_payload


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

    if not await check_user_update(message, state, command):
        return

    text = (
        "😊 <b>Sizni yana ko‘rishdan xursandmiz!</b>\n\n"
        "📌 <b>Botdan foydalanish uchun quyidagi tugmalardan foydalaning:</b>"
    )
    await message.answer(text=text, reply_markup=main_menu_kb)


async def check_user_update(
    message: types.Message, state: FSMContext, command: CommandObject
):
    user_data = {
        "username": message.from_user.username,
        "fullname": message.from_user.full_name,
    }

    user_info = await db.user_update(user_id=message.from_user.id, data=user_data)

    if user_info.get("input_fullname") is None:
        text = (
            "👋 <b>Xush kelibsiz!</b>\n\n"
            "🔹 Botdan foydalanish uchun avval <b>ro‘yxatdan o‘tishingiz</b> kerak.\n"
            "📝 Iltimos, <b>ism va familiyangizni</b> kiriting."
        )
        await message.answer(
            text=text,
            reply_markup=remove_kb,
        )
        await state.set_state(RegState.fullname)
        return False

    if user_info.get("input_phone") is None:
        text = (
            "📞 <b>Telefon raqamingizni kiriting!</b>\n\n"
            "🔹 <b>Qo‘lda yozish shart emas!</b>\n"
            '📲 <b>"Raqamni yuborish"</b> tugmasini bosing va avtomatik ravishda ma’lumotlaringizni jo‘nating.'
        )
        await message.answer(
            text=text,
            reply_markup=contact_kb,
        )
        await state.set_state(RegState.phone_number)
        return False

    if user_info.get("is_subscribed") is None:
        await message.answer_invoice(
            title="🎉 Xush kelibsiz!",
            description=(
                "🔹 <b>Botdan foydalanish uchun obuna bo‘lishingiz kerak.</b>\n"
                "📅 <b>Oylik obuna narxi:</b> 15,000 UZS\n\n"
                "💳 To‘lovni amalga oshirish uchun quyidagi tugmadan foydalaning."
            ),
            provider_token=conf.bot.payment_provider_token,
            currency="uzs",
            prices=[types.LabeledPrice(label="Oylik obuna", amount=15_000_00)],
            start_parameter="create_invoice",
            payload="subscription",
        )
        await state.set_state(RegState.subscription)
        return False

    return True


@start_router.message(Command("help"))
async def help_command(message: types.Message, state: FSMContext):
    text = (
        "🆘 <b>Yordam bo‘limi</b>\n\n"
        "🔹 Agar botdan foydalanishda muammolarga duch kelsangiz yoki qo‘shimcha savollaringiz bo‘lsa, biz sizga yordam bera olamiz.\n\n"
        "💡 <b>Asosiy buyruqlar:</b>\n"
        "👉 <code>/start</code> - Botni ishga tushirish\n"
        "👉 <code>/help</code> - Yordam olish\n"
        "❓ Qo‘shimcha savollaringiz bo‘lsa, administratorga murojaat qiling."
    )
    await message.answer(
        text=text,
        reply_markup=main_menu_kb,
    )
    return await state.clear()
