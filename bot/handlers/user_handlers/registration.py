from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from keyboards.common_kb import contact_kb, main_menu_kb
from structures.states import RegState
from structures.database import db
from configuration import conf

register_router = Router()


@register_router.message(RegState.fullname, ~F.text.startswith("/"))
async def input_firstname(message: types.Message, state: FSMContext):
    """Foydalanuvchi ismini qabul qilish"""
    await state.update_data(input_fullname=message.text)

    text = (
        "📞 <b>Telefon raqamingizni kiriting!</b>\n\n"
        "🔹 <b>Qo‘lda yozish shart emas!</b>\n"
        "📲 <b>\"Raqamni yuborish\"</b> tugmasini bosing va avtomatik ravishda ma’lumotlaringizni jo‘nating."
    )

    await message.answer(text=text, reply_markup=contact_kb(), parse_mode="HTML")
    await state.set_state(RegState.phone_number)


@register_router.message(RegState.phone_number, ~F.text.startswith("/") | F.text | F.contact)
async def input_phone(message: types.Message, state: FSMContext):
    """Telefon raqamini qabul qilish"""
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text
    else:
        return await message.answer("❌ <b>Noto‘g‘ri format!</b> Iltimos, telefon raqamingizni to‘g‘ri kiriting.", parse_mode="HTML")

    await state.update_data(input_phone=phone)

    text = (
        "🎉 <b>Xush kelibsiz!</b>\n\n"
        "🔹 Botdan foydalanish uchun siz obuna bo‘lishingiz kerak.\n"
        "💰 <b>Oylik obuna narxi:</b> <code>15,000 UZS</code>\n\n"
        "📌 <b>To‘lovni amalga oshirish uchun pastdagi tugmadan foydalaning.</b>"
    )
    await message.answer(text=text)

    await message.answer_invoice(
        title="🎉 Xush kelibsiz!",
        description="🔹 Botdan foydalanish uchun to‘lovni amalga oshiring.",
        provider_token=conf.bot.payment_provider_token,
        currency="uzs",
        prices=[types.LabeledPrice(label="Oylik obuna", amount=15_000_00)],
        start_parameter="create_invoice",
        payload="subscription",
    )
    return await state.set_state(RegState.subscription)
