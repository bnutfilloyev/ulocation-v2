from aiogram import types
from aiogram.fsm.context import FSMContext
from structures.states import RegState
from keyboards.common_kb import contact_kb, remove_kb
from keyboards.user_kb import language_kb
from configuration import conf
from structures.database import db
from aiogram.utils.i18n import gettext as _

async def check_user_stepwise(message: types.Message, state: FSMContext) -> bool:
    """Bosqichma-bosqich foydalanuvchi tekshiruvlari"""
    user_info = await db.user_update(user_id=message.chat.id)

    # Bosqichma-bosqich tekshiruv
    if user_info.get("language") is None:
        await message.answer(
            _("🌐 <b>Tilni tanlang!</b>\n\n"
              "🔹 <b>Botdan foydalanish uchun tilni tanlang:</b>"),
            reply_markup=language_kb()
        )
        return False

    if user_info.get("input_fullname") is None:
        await message.answer(
            _("👋 <b>Xush kelibsiz!</b>\n\n"
              "🔹 Botdan foydalanish uchun avval <b>ro‘yxatdan o‘tishingiz</b> kerak.\n"
              "📝 Iltimos, <b>ism va familiyangizni</b> kiriting."),
            reply_markup=remove_kb
        )
        await state.set_state(RegState.fullname)
        return False

    if user_info.get("input_phone") is None:
        await message.answer(
            _("📞 <b>Telefon raqamingizni kiriting!</b>\n\n"
              "🔹 <b>Qo‘lda yozish shart emas!</b>\n"
              '📲 <b>"Raqamni yuborish"</b> tugmasini bosing va avtomatik ravishda ma’lumotlaringizni jo‘nating.'),
            reply_markup=contact_kb
        )
        await state.set_state(RegState.phone_number)
        return False

    if user_info.get("is_subscribed") is None or not user_info.get("is_subscribed"):
        await message.answer_invoice(
            title=_("🎉 Xush kelibsiz!"),
            description=_(
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