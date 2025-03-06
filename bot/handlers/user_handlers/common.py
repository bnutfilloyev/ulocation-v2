from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from keyboards.common_kb import contact_kb, main_menu_kb, remove_kb
from structures.database import db
from structures.states import RegState, BroadcastState
from configuration import conf

start_router = Router()


@start_router.message(Command("start"))
async def start_command(
    message: types.Message, state: FSMContext, command: CommandObject
):
    """Start command."""
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
        await message.answer(text=text, reply_markup=remove_kb(), parse_mode="HTML")
        return await state.set_state(RegState.fullname)

    if user_info.get("input_phone") is None:
        text = (
            "📞 <b>Telefon raqamingizni kiriting!</b>\n\n"
            "🔹 <b>Qo‘lda yozish shart emas!</b>\n"
            "📲 <b>\"Raqamni yuborish\"</b> tugmasini bosing va avtomatik ravishda ma’lumotlaringizni jo‘nating."
        )
        await message.answer(text=text, reply_markup=contact_kb(), parse_mode="HTML")
        return await state.set_state(RegState.phone_number)

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
        return await state.set_state(RegState.subscription)

    text = (
        "😊 <b>Sizni yana ko‘rishdan xursandmiz!</b>\n\n"
        "📌 <b>Botdan foydalanish uchun quyidagi tugmalardan birini tanlang:</b>"
    )
    await message.answer(text=text, reply_markup=main_menu_kb(), parse_mode="HTML")


@start_router.message(Command("help"))
async def help_command(message: types.Message, state: FSMContext):
    """Help command."""
    text = (
        "🆘 <b>Yordam bo‘limi</b>\n\n"
        "🔹 Agar botdan foydalanishda muammolarga duch kelsangiz yoki qo‘shimcha savollaringiz bo‘lsa, biz sizga yordam bera olamiz.\n\n"
        "💡 <b>Asosiy buyruqlar:</b>\n"
        "👉 <code>/start</code> - Botni ishga tushirish\n"
        "👉 <code>/help</code> - Yordam olish\n"
        "👉 <code>/broadcast</code> - Xabar jo‘natish (Adminlar uchun)\n\n"
        "❓ Qo‘shimcha savollaringiz bo‘lsa, administratorga murojaat qiling."
    )
    await message.answer(text=text, reply_markup=main_menu_kb(), parse_mode="HTML")
    return await state.clear()