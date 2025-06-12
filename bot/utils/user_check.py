from datetime import datetime

from aiogram import Bot, types
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.deep_linking import decode_payload
from configuration import conf
from database import referral_db, user_db
from keyboards.common_kb import agreement_kb, contact_kb, link_kb, remove_kb
from keyboards.user_kb import language_kb
from structures.states import RegState, PaymentState


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
        "🎯<b>Eslatma:</b> Bonuslaringiz siz botga obuna bo‘lgandan so‘ng avtomatik ravishda qo‘shiladi."
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

    if user_info.get("agreement") is None:
        text = (
            "📝 <b>Xizmatdan foydalanishdan oldin, iltimos bizning ommaviy oferta shartlarimiz bilan tanishing.</b>\n\n"
            "⬇️ Quyida ommaviy oferta shartlari PDF formatida yuborilgan.\n\n"
            "✅ Oferta shartlarini o'qib chiqib, \"Roziman\" tugmasini bosing."
        )
        
        await message.answer(text=text)
        oferta = FSInputFile("files/oferta.pdf", filename="agreement.pdf")
        await message.answer_document(
            document=oferta,
            caption="📄 Ommaviy oferta shartlari",
            reply_markup=agreement_kb(),
        )
    
        await state.set_state(RegState.agreement)
        return False
    
    # Registration is complete - user can now use basic features
    # Payment is only required for premium features (promotions)

    return True


async def check_user_premium_access(message: types.Message, state: FSMContext) -> bool:
    """Check if user has premium subscription for accessing promotions"""
    user_info = await user_db.user_update(user_id=message.chat.id)
    
    # Check if user is subscribed
    if not user_info.get("is_subscribed"):
        premium_text = (
            "🎯 <b>Premium bo'limga xush kelibsiz!</b>\n\n"
            "Bu bo'lim faqat premium a'zolar uchun mo'ljallangan. "
            "Premium obuna bilan siz quyidagi imkoniyatlarga ega bo'lasiz:\n\n"
            
            "💎 <b>Eksklyuziv aksiyalar va chegirmalar</b>\n"
            "🎁 <b>Maxsus promokodlar</b>\n"
            "💰 <b>100$ dan ortiq chegirmalar</b>\n"
            "🆓 <b>Bepul mahsulotlar va xizmatlar</b>\n"
            "🏪 <b>Kafelar, salonlar, dorixonalarda bonuslar</b>\n\n"
            
            "✨ Premium obuna bo'lish uchun quyidagi tugmani bosing!"
        )
        
        await message.answer(premium_text, reply_markup=link_kb)
        
        invoice_description = (
            "🎯 PREMIUM CLUB — Ulocation\n\n"
            "✅ 100$ dan ortiq chegirmalar\n"
            "✅ Eksklyuziv promokodlar\n"
            "✅ Bepul mahsulotlar va xizmatlar\n"
            "✅ Kafelar, salonlar, dorixonalarda maxsus takliflar\n"
            "✅ SPA va fitnes zallar uchun kuponlar\n\n"
            "Premium a'zo bo'ling va barcha imkoniyatlardan foydalaning!"
        )
        
        await message.answer_invoice(
            title="💎 PREMIUM CLUB — Ulocation",
            description=invoice_description,
            provider_token=conf.bot.payment_provider_token,
            currency="uzs",
            prices=[types.LabeledPrice(label=("Premium obuna"), amount=15_000_00)],
            start_parameter="premium_subscription",
            payload="premium_subscription",
        )
        await state.set_state(RegState.subscription)
        return False
    
    # Check subscription expiry date (same logic as in check_user_stepwise)
    if "expiry_date" in user_info:
        expiry_date = user_info["expiry_date"].get("$date", None) if isinstance(user_info["expiry_date"], dict) else user_info.get("expiry_date")
        
        if expiry_date:
            # Convert string to datetime if it's a string
            if isinstance(expiry_date, str):
                try:
                    expiry_date = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                except ValueError:
                    # If invalid date format, treat as expired
                    expiry_date = datetime.min
            
            current_time = datetime.now().replace(tzinfo=None)
            expiry_time = expiry_date.replace(tzinfo=None) if hasattr(expiry_date, 'replace') else datetime.min
            
            # If subscription expired
            if current_time > expiry_time:
                renewal_text = (
                    "⚠️ <b>Sizning Premium obunangiz muddati tugagan!</b>\n\n"
                    "🔄 Premium imkoniyatlardan foydalanishni davom ettirish uchun obunani yangilang.\n\n"
                    
                    "💎 <b>Premium obuna imkoniyatlari:</b>\n"
                    "— 100$ dan ortiq chegirmalar\n"
                    "— Eksklyuziv promokodlar\n"
                    "— Bepul mahsulotlar va xizmatlar\n"
                    "— Kafelar, salonlar, dorixonalarda maxsus takliflar\n\n"
                    
                    "💰 <b>Oylik obuna narxi:</b> <code>15,000 UZS</code>\n\n"
                    "📌 <b>Obunani yangilash uchun quyidagi tugmadan foydalaning.</b>"
                )
                
                await message.answer(renewal_text, reply_markup=link_kb)
                
                renewal_description = (
                    "🔄 Premium obunani yangilab, barcha imkoniyatlardan yana foydalaning:\n\n"
                    "✅ 100$ dan ortiq chegirmalar\n"
                    "✅ Eksklyuziv promokodlar\n"
                    "✅ Bepul mahsulotlar va xizmatlar\n"
                    "✅ Hamkorlarimizdan maxsus takliflar\n\n"
                    "💎 PREMIUM CLUB — Ulocation"
                )
                
                await message.answer_invoice(
                    title="🔄 Premium obunani yangilash",
                    description=renewal_description,
                    provider_token=conf.bot.payment_provider_token,
                    currency="uzs",
                    prices=[types.LabeledPrice(label=("Premium obuna"), amount=15_000_00)],
                    start_parameter="renew_premium_subscription",
                    payload="premium_subscription_renewal",
                )
                await state.set_state(RegState.subscription)
                return False
    
    return True