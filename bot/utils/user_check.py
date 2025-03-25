from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import  CommandObject
from aiogram.utils.deep_linking import decode_payload


from configuration import conf
from database import user_db, referral_db
from keyboards.common_kb import contact_kb, remove_kb
from keyboards.user_kb import language_kb
from structures.states import RegState


async def check_user_referral(message: types.Message, command: CommandObject, bot: Bot) -> bool:
    if not command.args:
        return
    
    referrer_id = decode_payload(command.args)
    if not referrer_id:
        return await message.answer(
            "❌ <b>Uzr, bu havola noto‘g‘ri yoki muddati tugagan!</b>\n\n"
            "🔎 Iltimos, havolangizni tekshiring va qaytadan urinib ko‘ring."
        )
    
    if not await referral_db.add_referral(user_id=message.from_user.id, referrer_id=referrer_id):
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


async def check_user_stepwise(message: types.Message, state: FSMContext) -> bool:
    """Bosqichma-bosqich foydalanuvchi tekshiruvlari"""
    user_info = await user_db.user_update(user_id=message.chat.id)

    if user_info.get("language") is None:
        await message.answer(
            "🌐 <b>Tilni tanlang!</b>\n\n"
            "🔹 <b>Botdan foydalanish uchun tilni tanlang:</b>",
            reply_markup=language_kb()
        )
        return False

    if user_info.get("input_fullname") is None:
        await message.answer((
            "👋 <b>Xush kelibsiz!</b>\n\n"
            "🔹 Botdan foydalanish uchun avval <b>ro‘yxatdan o‘tishingiz</b> kerak.\n"
            "📝 Iltimos, <b>ism va familiyangizni</b> kiriting."),
            reply_markup=remove_kb
        )
        await state.set_state(RegState.fullname)
        return False

    if user_info.get("input_phone") is None:
        await message.answer(
            ("📞 <b>Telefon raqamingizni kiriting!</b>\n\n"
              "🔹 <b>Qo‘lda yozish shart emas!</b>\n"
              '📲 <b>"Raqamni yuborish"</b> tugmasini bosing va avtomatik ravishda ma’lumotlaringizni jo‘nating.'),
            reply_markup=contact_kb
        )
        await state.set_state(RegState.phone_number)
        return False

    if user_info.get("is_subscribed") is None or not user_info.get("is_subscribed"):
        await message.answer_invoice(
            title="🎉 Xush kelibsiz!",
            description=(
                "🔹 <b>Botdan foydalanish uchun obuna bo‘lishingiz kerak.</b>\n"
                "📅 <b>Oylik obuna narxi:</b> 15,000 UZS\n\n"
                "💳 To‘lovni amalga oshirish uchun quyidagi tugmadan foydalaning."
            ),
            provider_token=conf.bot.payment_provider_token,
            currency="uzs",
            prices=[types.LabeledPrice(label=_("Oylik obuna"), amount=15_000_00)],
            start_parameter="create_invoice",
            payload="subscription",
        )
        await state.set_state(RegState.subscription)
        return False

    return True