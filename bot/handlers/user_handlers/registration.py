from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from configuration import conf
from keyboards.common_kb import contact_kb, main_menu_kb
from keyboards.user_kb import  LanguageCD
from structures.database import db
from structures.states import RegState
from aiogram.utils.i18n import gettext as _
from utils.user_check import check_user_stepwise

register_router = Router()


@register_router.callback_query(LanguageCD.filter())
async def set_language(query: types.CallbackQuery, callback_data: LanguageCD, state: FSMContext):   
    await state.clear()
    await db.user_update(user_id=query.from_user.id, data={"language": callback_data.lang})
    await query.message.delete()

    if not await check_user_stepwise(query.message, state):  
        return
    
    text = (
        "😊 <b>Sizni yana ko‘rishdan xursandmiz!</b>\n\n"
        "📌 <b>Botdan foydalanish uchun quyidagi tugmalardan foydalaning:</b>"
    )
    await query.message.answer(text=_(text), reply_markup=main_menu_kb)
    

@register_router.message(RegState.fullname, ~F.text.startswith("/"))
async def input_firstname(message: types.Message, state: FSMContext):
    """Foydalanuvchi ismini qabul qilish"""
    await state.update_data(input_fullname=message.text)

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


@register_router.message(
    RegState.phone_number, ~F.text.startswith("/") | F.text | F.contact
)
async def input_phone(message: types.Message, state: FSMContext):
    """Telefon raqamini qabul qilish"""
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text
    else:
        return await message.answer(
            "❌ <b>Noto‘g‘ri format!</b> Iltimos, telefon raqamingizni to‘g‘ri kiriting.",
        )

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
