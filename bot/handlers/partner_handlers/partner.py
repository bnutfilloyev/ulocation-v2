from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import partner_db, promotion_db
from keyboards.common_kb import remove_kb
from keyboards.partner_kb import PartnerMenuCD, get_partner_promotions_kb, partner_menu_kb
from structures.states import AddPromotionState, PartnerAuthState


partner_router = Router()


@partner_router.message(Command("partner"))
async def partner_command(message: types.Message, state: FSMContext):
    """Partnyor login oynasi"""
    await message.answer(
        "🔐 <b>Partnyor sifatida tizimga kirish</b>\n\n"
        "📝 Iltimos, sizga berilgan <b>login</b>ni kiriting:",
    )
    await state.set_state(PartnerAuthState.waiting_for_partner_login)


@partner_router.message(PartnerAuthState.waiting_for_partner_login)
async def process_partner_login(message: types.Message, state: FSMContext):
    """Loginni tekshirish"""
    login = message.text.strip()
    await state.update_data(login=login)
    await message.answer(
        "🔑 <b>Endi parolingizni kiriting:</b>",
    )
    await state.set_state(PartnerAuthState.waiting_for_partner_password)


@partner_router.message(PartnerAuthState.waiting_for_partner_password)
async def process_partner_password(message: types.Message, state: FSMContext):
    """Login va parolni tekshirish"""
    data = await state.get_data()
    partner = await partner_db.check_partner_credentials(login=data.get("login"), password=message.text.strip())

    if partner is None:
        await message.answer(
            "❌ <b>Login yoki parol noto‘g‘ri!</b>\n\n"
            "Iltimos, qayta urinib ko‘ring.",
        )
        return await state.clear()

    text = (
        "✅ <b>Partnyor sifatida tizimga muvaffaqiyatli kirdingiz!</b>\n\n"
        "⚙️ <b>Quyidagi tugmalardan birini tanlang:</b>"
    )
    btn = await partner_menu_kb(partner.get("_id"))
    await message.answer(
        text=text,
        reply_markup=btn,
    )
    return await state.clear()


@partner_router.callback_query(PartnerMenuCD.filter(F.action == "add_promotion"))
async def start_add_promotion(
    callback_query: types.CallbackQuery, state: FSMContext, callback_data: PartnerMenuCD
):
    """Yangi aksiya qo‘shish"""
    partner_id = callback_data.partner_id
    await state.update_data(partner_id=partner_id)

    await callback_query.message.answer(
        "🎉 <b>Yangi aksiyani yaratamiz!</b>\n\n"
        "📌 <b>Aksiya nomi:</b> Iltimos, aksiyangiz nomini kiriting.\n"
        "✏️ <i>Misol:</i> 'Tezkor Cashback 20%', 'Bepul Kofe', 'Super Sovg‘alar'...",
    )
    await state.set_state(AddPromotionState.waiting_for_promotion_name)
    await callback_query.answer()


@partner_router.message(AddPromotionState.waiting_for_promotion_name)
async def process_promotion_name(message: types.Message, state: FSMContext):
    """Aksiya nomini qabul qilish"""
    promo_name = message.text.strip()
    await state.update_data(promo_name=promo_name)
    await message.answer(
        "📝 <b>Aksiya tavsifi:</b>\n\n"
        "📄 Aksiya haqida batafsil ma’lumot kiriting.\n"
        "🔹 <i>Qanday imtiyozlar mavjud?</i>\n"
        "🔹 <i>Kimlar uchun amal qiladi?</i>\n"
        "🔹 <i>Qanday shartlar bor?</i>\n\n"
        "🖋 <i>Misol:</i> 'Ushbu aksiya faqat yangi mijozlar uchun amal qiladi. Xizmatdan 1 marta foydalanish mumkin.'",
    )
    await state.set_state(AddPromotionState.waiting_for_promotion_description)


@partner_router.message(AddPromotionState.waiting_for_promotion_description)
async def process_promotion_description(message: types.Message, state: FSMContext):
    """Aksiya tavsifini qabul qilish"""
    promo_description = message.text.strip()
    await state.update_data(promo_description=promo_description)

    await message.answer(
        "📦 <b>Aksiya turini tanlang</b>\n\n"
        "🔸 <i>Misol:</i> 'Chegirma', 'Sovg‘a', 'Cashback', 'Bonus'...",
        reply_markup=remove_kb,
    )
    await state.set_state(AddPromotionState.waiting_for_promotion_category)


@partner_router.message(AddPromotionState.waiting_for_promotion_category)
async def process_promotion_category(message: types.Message, state: FSMContext):
    """Aksiya turini qabul qilish va DBga qo‘shish"""
    category = message.text.strip()
    await state.update_data(category=category)

    data = await state.get_data()
    promo_id = await promotion_db.add_promotion(
        partner_id=data["partner_id"],
        name=data["promo_name"],
        description=data["promo_description"],
        category=data["category"],
    )

    if not promo_id:
        await message.answer(
            "❌ <b>Xatolik yuz berdi.</b> Iltimos, qayta urinib ko‘ring.",
        )
        return await state.clear()

    btn = await partner_menu_kb(data["partner_id"])
    text = f"✅ <b>Aksiya '{data['promo_name']}' muvaffaqiyatli qo‘shildi!</b>"
    await message.answer(text, reply_markup=btn)

    await state.clear()



@partner_router.callback_query(PartnerMenuCD.filter(F.action == "finish_promotion"))
async def select_promotion_to_finish(
    callback_query: types.CallbackQuery, callback_data: PartnerMenuCD
):
    """Faol aksiyalarni tugatish"""
    partner_id = callback_data.partner_id
    promotions = await promotion_db.get_active_promotions(partner_id)

    if not promotions:
        await callback_query.message.answer(
            "❌ <b>Sizning faol aksiyalaringiz yo‘q.</b>\n\n"
            "🔹 Yangi aksiya yaratish uchun: <b>'Aksiya yaratish'</b> tugmasini bosing.",
        )
        await callback_query.answer()
        return

    text = "🛑 <b>Aksiya tugatish</b>\n\n📋 <b>Faol aksiyalaringiz ro‘yxati:</b>\n\n🔽 Tugatmoqchi bo‘lgan aksiyangizni tanlang."
    btn = await get_partner_promotions_kb(promotions)
    await callback_query.message.answer(
        text,
        reply_markup=btn,
    )
    await callback_query.answer()


@partner_router.callback_query(PartnerMenuCD.filter(F.action == "reports"))
async def show_reports(
    callback_query: types.CallbackQuery, callback_data: PartnerMenuCD
):
    """Hisobotlar"""
    await callback_query.message.answer(
        "📊 <b>Hisobotlar bo‘limi tez orada qo‘shiladi...</b>",
    )
    await callback_query.answer()


@partner_router.callback_query(PartnerMenuCD.filter(F.action == "check_promo_code"))
async def check_promo_code_start(
    callback_query: types.CallbackQuery, state: FSMContext
):
    """Promokod tekshirishni boshlash"""
    await callback_query.message.answer(
        "🔎 <b>Promokodni kiriting:</b>\n\n"
        "💬 Iltimos, mijozdan olgan promokodni yuboring.",
    )
    await state.set_state(PartnerAuthState.waiting_for_promo_code)
    await callback_query.answer()


@partner_router.message(PartnerAuthState.waiting_for_promo_code)
async def process_promo_code(message: types.Message, state: FSMContext):
    """Promokodni qabul qilish va tekshirish"""
    promo_code = message.text.strip()

    promo = await promotion_db.check_promo_code(promo_code)
    if promo is None:
        await message.answer(
            "❌ <b>Promokod topilmadi!</b>\n\n"
            "Iltimos, to‘g‘ri promokod yuboring yoki mijozdan tekshirib qaytadan urinib ko‘ring.",
        )
        return await state.clear()

    marks_promo_code_as_used = await promotion_db.mark_promo_code_as_used(promo_code)
    if not marks_promo_code_as_used:
        await message.answer(
            "❌ <b>Promokod allaqachon ishlatilgan!</b>\n\n"
            "Iltimos, mijozdan tekshirib qaytadan urinib ko‘ring.",
        )
        return await state.clear()

    text = (
        f"✅ <b>Promokod tasdiqlandi!</b>\n\n"
        f"📌 <b>Aksiya nomi:</b> {promo['promotion']['name']}\n"
        f"📖 <b>Tavsif:</b> {promo['promotion']['description']}\n"
        f"🏷 <b>Kategoriya:</b> {promo['promotion']['category']}\n"
        f"🆔 <b>Promokod:</b> {promo['code']}\n\n"
        f"🎁 Ushbu promokodni mijoz foydalanishi mumkin."
    )

    await promotion_db.mark_promo_code_as_used(promo_code)

    await message.answer(text)
    await state.clear()
