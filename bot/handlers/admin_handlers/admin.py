from aiogram import F, Router, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from keyboards.common_kb import (
    PartnerCD,
    admin_menus_kb,
    admin_partner_menus_kb,
    get_partner_kb,
)
from structures.database import db
from structures.states import PartnerAddState

admin_router = Router()


@admin_router.message(Command("access"))
async def access_by_userid(message: types.Message, command: CommandObject):
    """Admin huquqlarini foydalanuvchiga berish"""
    user_id = command.args

    if not user_id:
        return await message.answer(
            f"🔐 <b>Sizning Telegram ID-ingiz:</b> <code>{message.from_user.id}</code>\n\n"
            "👤 Admin huquqini berish uchun quyidagi buyruqni ishlating:\n"
            "<code>/access [user_id]</code>\n"
            "Misol: <code>/access 123456789</code>",
            parse_mode="HTML",
        )

    await db.user_update(user_id, {"is_admin": True})
    await message.answer(
        f"✅ <code>{str(user_id)}</code> foydalanuvchi endi admin sifatida belgilandi.",
        parse_mode="HTML",
    )


@admin_router.message(Command("admin"))
async def admin_command(message: types.Message, state: FSMContext):
    """Admin paneliga kirish"""
    user_update = await db.user_update(message.from_user.id)

    if not user_update.get("is_admin"):
        await message.answer(
            f"🚫 <b>Ruxsat berilmadi!</b>\n\n"
            f"❌ <code>{message.from_user.id}</code> foydalanuvchi admin emas.",
            parse_mode="HTML",
        )
        return await state.clear()

    await state.clear()
    text = (
        "🎛 <b>Admin paneliga muvaffaqiyatli kirdingiz!</b>\n\n"
        "ℹ️ Quyidagi tugmalardan birini tanlab, kerakli bo‘limga o‘ting:"
    )
    await message.answer(text, reply_markup=admin_menus_kb(), parse_mode="HTML")


@admin_router.callback_query(F.data == "admin_partner_settings")
async def partner_management_menu(callback_query: types.CallbackQuery):
    """Partnerlarni boshqarish menyusi"""
    await callback_query.message.edit_text(
        "🛠 <b>Partnerlarni boshqarish bo‘limi</b>\n\n"
        "Quyidagi tugmalardan birini tanlang ⬇️",
        reply_markup=admin_partner_menus_kb(),
        parse_mode="HTML",
    )
    await callback_query.answer()


@admin_router.callback_query(F.data == "admin_partner_add")
async def start_partner_add(callback_query: types.CallbackQuery, state: FSMContext):
    """Yangi partnyor qo‘shish"""
    await callback_query.message.answer(
        "📝 <b>Yangi partnyor qo‘shamiz!</b>\n\n"
        "👤 Iltimos, partnyorning <b>nomini</b> kiriting:",
        parse_mode="HTML",
    )
    await state.set_state(PartnerAddState.waiting_for_partner_name)
    await callback_query.answer()


@admin_router.message(PartnerAddState.waiting_for_partner_name)
async def process_partner_name(message: types.Message, state: FSMContext):
    """Partnyorning nomini saqlash"""
    partner_name = message.text.strip()
    await state.update_data(partner_name=partner_name)
    await message.answer(
        "📌 Endi partnyor uchun <b>login</b> kiriting:", parse_mode="HTML"
    )
    await state.set_state(PartnerAddState.waiting_for_partner_login)


@admin_router.message(PartnerAddState.waiting_for_partner_login)
async def process_partner_login(message: types.Message, state: FSMContext):
    """Partnyor logini qabul qilish"""
    partner_login = message.text.strip()
    await state.update_data(partner_login=partner_login)
    await message.answer(
        "🔑 Endi partnyor uchun <b>parol</b> kiriting:", parse_mode="HTML"
    )
    await state.set_state(PartnerAddState.waiting_for_partner_password)


@admin_router.message(PartnerAddState.waiting_for_partner_password)
async def process_partner_password(message: types.Message, state: FSMContext):
    """Partnyor parolini saqlash va DB ga qo‘shish"""
    partner_password = message.text.strip()
    await state.update_data(partner_password=partner_password)

    partner_data = await state.get_data()
    inserted = await db.add_partner(partner_data)

    if not inserted:
        await message.answer(
            "❌ <b>Xatolik!</b>\n\n"
            "Bu login bilan partnyor allaqachon mavjud. Iltimos, boshqa login tanlang.",
            parse_mode="HTML",
        )
        return await state.clear()

    text = (
        "✅ <b>Partnyor muvaffaqiyatli qo‘shildi!</b>\n\n"
        f"👤 <b>Ism:</b> {partner_data.get('partner_name')}\n"
        f"🔑 <b>Login:</b> {partner_data.get('partner_login')}\n"
        f"🛡 <b>Parol:</b> {partner_data.get('partner_password')}\n\n"
        "📌 Partnyorga ushbu ma'lumotlarni yetkazing."
    )
    await message.answer(text, parse_mode="HTML")
    return await state.clear()


@admin_router.callback_query(F.data == "admin_partner_delete")
async def show_partner_delete_list(callback_query: types.CallbackQuery):
    """Partnyor o‘chirish menyusi"""
    partners = await db.get_parners()

    if not partners:
        await callback_query.message.answer(
            "❌ <b>Hozirda hech qanday partnyor mavjud emas.</b>", parse_mode="HTML"
        )
        return await callback_query.answer()

    text = "🗑 <b>O‘chirmoqchi bo‘lgan partnyoringizni tanlang:</b>"
    btn = await get_partner_kb(partners)
    await callback_query.message.answer(text, reply_markup=btn, parse_mode="HTML")
    await callback_query.answer()


@admin_router.callback_query(PartnerCD.filter())
async def partner_delete_handler(
    callback_query: types.CallbackQuery, callback_data: PartnerCD
):
    """Partnyorni o‘chirish"""
    partner_login = callback_data.partner_login
    if callback_data.action == "delete":
        result = await db.db.partners.delete_one({"partner_login": partner_login})
        if result.deleted_count:
            await callback_query.message.answer(
                f"✅ <b>Partnyor '{partner_login}' muvaffaqiyatli o‘chirildi!</b>",
                parse_mode="HTML",
            )
        else:
            await callback_query.message.answer(
                "❌ <b>Xatolik yuz berdi!</b>\n\n"
                "Bunday partnyor topilmadi yoki o‘chirishda muammo yuzaga keldi.",
                parse_mode="HTML",
            )
    return await callback_query.answer()
