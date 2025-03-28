from datetime import datetime, timedelta

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PreCheckoutQuery
from database import referral_db, user_db
from dateutil.relativedelta import relativedelta
from keyboards.common_kb import main_menu_kb
from structures.states import RegState

invoices_router = Router()


@invoices_router.pre_checkout_query(RegState.subscription, F.invoice_payload == "subscription")
async def pre_checkout_query(query: PreCheckoutQuery) -> None:
    await query.answer(ok=True)


@invoices_router.message(RegState.subscription, F.successful_payment)
async def successful_payment(message: Message, state: FSMContext, bot: Bot) -> None:
    now = datetime.now()
    user = await user_db.user_update(user_id=message.from_user.id)

    if user.get("expiry_date") and user["expiry_date"] > now:
        new_expiry = user["expiry_date"] + relativedelta(months=1)
    else:
        new_expiry = now + relativedelta(months=1)

    payment_amount = message.successful_payment.total_amount / 100
    currency = message.successful_payment.currency

    payment_log = {
        "payment_id": message.successful_payment.invoice_payload,
        "payment_date": now,
        "amount": payment_amount,
        "currency": currency,
    }

    update_data = {
        "username": message.from_user.username,
        "is_subscribed": True,
        "expiry_date": new_expiry,
        "payments": user.get("payments", []) + [payment_log],
    }

    await user_db.user_update(user_id=message.from_user.id, data=update_data)

    await message.answer(
        f"🎉 <b>To'lov muvaffaqiyatli amalga oshirildi!</b>\n\n"
        f"📅 <b>Obunangiz</b> <code>{new_expiry.strftime('%d-%m-%Y')}</code> gacha amal qiladi.\n\n"
        "✅ Endi botimizning barcha imkoniyatlaridan bemalol foydalanishingiz mumkin!\n\n"
        "🔽 Quyidagi tugmalardan birini tanlang:",
        reply_markup=main_menu_kb,
    )

    await referral_db.process_referral_payment(user_id=message.from_user.id)
    referrer_id = await referral_db.get_referrer(user_id=message.from_user.id)
    
    if referrer_id:
        await bot.send_message(
            referrer_id,
            f"💰 Sizning referral havolangiz orqali foydalanuvchi "
            f"<b>{message.from_user.full_name}</b> obuna bo‘ldi!"
        )
