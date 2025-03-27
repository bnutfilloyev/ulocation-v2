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

    if user_info.get("is_subscribed") is None or not user_info.get("is_subscribed"):
        welcome_text = (
            "Assalomu alaykum!\n"
            "Xush kelibsiz @ulocationbot ga!\n"
            "Siz endi O'zbekiston bo'ylab yagona chegirma va bonus lokatsiyalar xizmati bilan tanishmoqdasiz!\n\n"
            
            "📍 <b>Nima bu bot?</b>\n"
            "Bu bot orqali siz har oy atigi 15 000 so'm evaziga:\n"
            "— 100$ dan ortiq chegirmalar,\n"
            "— bepul mahsulotlar va xizmatlar,\n"
            "— va turli lokatsiyalar haqida ma'lumotlarga ega bo'lasiz!\n\n"
            
            "💼 <b>Bizning hamkorlarimiz:</b>\n"
            "Kafelar, go'zallik salonlari, dorixonalar, klinikalar, xizmat ko'rsatish markazlari va boshqalar!\n\n"
            
            "🎁 <b>Siz uchun tayyorlangan imkoniyatlar:</b>\n"
            "— Bepul qahvalar\n"
            "— Chegirmali burgerlar\n"
            "— Go'zallik salonlarida maxsus narxlar\n"
            "— Dorixonalarda aksiya mahsulotlar\n"
            "— SPA va fitnes zallar uchun kuponlar\n"
            "— va yana ko'plab ajoyib takliflar!\n\n"
            
            "🗺 <b>Bundan tashqari:</b>\n"
            "Har xil turdagi lokatsiyalar haqida faktlar, tavsiyalar, yangiliklar va foydali kontentni ham olasiz!\n\n"
            
            "✅ A'zo bo'lish uchun \"Obuna bo'lish\" tugmasini bosing va 15 000 so'm to'lovni amalga oshiring.\n"
            "Shundan so'ng barcha chegirmalar va bonuslar siz uchun ochiladi!\n\n"
            
            "<b>Ulocation — joyni bilgan yutadi!</b>"
        )
        
        await message.answer(welcome_text, reply_markup=link_kb)
        
        invoice_description = (
            "✅ 100$ dan ortiq chegirmalar\n"
            "✅ Bepul mahsulotlar va xizmatlar\n"
            "✅ Turli lokatsiyalar haqida foydali ma'lumotlar\n"
            "✅ Hamkorlarimizdan maxsus takliflar va bonuslar\n\n"
            "To'lovni amalga oshirgach, botning barcha imkoniyatlaridan foydalanishingiz mumkin!"
        )
        
        await message.answer_invoice(
            title="🎉 Ulocation — Joyni bilgan yutadi!",
            description=invoice_description,
            provider_token=conf.bot.payment_provider_token,
            currency="uzs",
            prices=[types.LabeledPrice(label=("Oylik obuna"), amount=15_000_00)],
            start_parameter="create_invoice",
            payload="subscription",
        )
        await state.set_state(RegState.subscription)
        return False
    
    # Check subscription expiry date
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
                    "⚠️ <b>Sizning obunangiz muddati tugagan!</b>\n\n"
                    "🔄 Xizmatdan foydalanishni davom ettirish uchun qayta to'lov qilishingiz kerak.\n\n"
                    
                    "📍 <b>Obunani yangilab, quyidagi imkoniyatlardan foydalaning:</b>\n"
                    "— 100$ dan ortiq chegirmalar\n"
                    "— Bepul mahsulotlar va xizmatlar\n"
                    "— Turli lokatsiyalar haqida ma'lumotlar\n"
                    "— Kafelar, go'zallik salonlari, dorixonalar va boshqa joylarda maxsus takliflar\n\n"
                    
                    "💰 <b>Oylik obuna narxi:</b> <code>15,000 UZS</code>\n\n"
                    "📌 <b>To'lovni amalga oshirish uchun quyidagi tugmadan foydalaning.</b>"
                )
                
                await message.answer(renewal_text)
                
                renewal_description = (
                    "🔄 Obunani yangilab, barcha imkoniyatlardan yana foydalaning:\n\n"
                    "✅ 100$ dan ortiq chegirmalar\n"
                    "✅ Bepul mahsulotlar va xizmatlar\n"
                    "✅ Turli lokatsiyalar haqida foydali ma'lumotlar\n"
                    "✅ Hamkorlarimizdan maxsus takliflar\n\n"
                    "Ulocation — joyni bilgan yutadi!"
                )
                
                await message.answer_invoice(
                    title="🔄 Obunani yangilash - Ulocation",
                    description=renewal_description,
                    provider_token=conf.bot.payment_provider_token,
                    currency="uzs",
                    prices=[types.LabeledPrice(label=("Oylik obuna"), amount=15_000_00)],
                    start_parameter="renew_subscription",
                    payload="subscription_renewal",
                    reply_markup=link_kb
                )
                await state.set_state(RegState.subscription)
                return False

    return True