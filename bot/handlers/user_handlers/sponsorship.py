from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from keyboards.common_kb import skip_kb, main_menu_kb
from structures.states import SponsorshipForm
from database import user_db
from aiogram.filters import Command, CommandObject


router = Router()


ADMIN_GROUP_ID = -1001566978667

@router.message(F.text == "🤝 Hamkor bo'lish")
async def sponsorship(message: types.Message, state: FSMContext):
    user_info = await user_db.user_update(message.from_user.id)
    fullname = user_info.get('input_fullname')
    await message.answer(
        f"🤝 <b>Hamkorlik imkoniyati!</b>\n\n"
        f"Assalomu alaykum, <b>{fullname}</b>!\n\n"
        f"Agar biz bilan hamkorlik qilish niyatida bo‘lsangiz, iltimos quyidagi ma’lumotlarni bizga yuboring.\n\n"
        f"🔗 Ijtimoiy tarmoqlardagi profilingiz havolalarini yuboring.\n"
        f"(Masalan: Instagram, Telegram, Facebook va boshqalar)"
    )
    await state.set_state(SponsorshipForm.social_links)

@router.message(SponsorshipForm.social_links)
async def process_social_links(message: types.Message, state: FSMContext):
    await state.update_data(social_links=message.text)
    await message.answer(
        "ℹ️ Agar qo‘shimcha fikr yoki takliflaringiz bo‘lsa, shu yerga yozing.\n"
        "(Ixtiyoriy, lekin biz uchun muhim bo‘lishi mumkin!)",
        reply_markup=skip_kb
    )
    await state.set_state(SponsorshipForm.additional_info)

@router.message(SponsorshipForm.additional_info)
async def process_additional_info(message: types.Message, state: FSMContext):
    user_info = await user_db.user_update(message.from_user.id)
    
    await state.update_data(additional_info=message.text)
    user_data = await state.get_data()

    # Format data for sending to admin group
    user_mention = f"@{message.from_user.username}" if message.from_user.username else f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>"
    
    sponsor_info = (
        f"📥 <b>Yangi hamkorlik so‘rovi!</b>\n\n"
        f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"
        f"👤 <b>Foydalanuvchi:</b> {user_mention}\n"
        f"📝 <b>Ismi:</b> {user_info['input_fullname']}\n"
        f"📱 <b>Telefon:</b> {user_info['input_phone']}\n"
        f"🔗 <b>Ijtimoiy tarmoqlar:</b> {user_data['social_links']}\n"
        f"ℹ️ <b>Qo‘shimcha ma’lumot:</b> {user_data['additional_info'] or 'Ko‘rsatilmagan'}"
    )
    

    await message.bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text=sponsor_info,
        parse_mode="HTML"
    )
    
    # Notify user about successful submission
    await message.answer(
        "✅ <b>So‘rovingiz qabul qilindi!</b>\n\n"
        "Tez orada jamoamiz siz bilan bog‘lanadi.\n"
        "Hamkorligingiz uchun samimiy minnatdorchilik bildiramiz! 🙏", 
        reply_markup=main_menu_kb
    )
    # Clear state
    await state.clear()

@router.message(Command("sponsorship"))
async def get_statistics(message: types.Message, state: FSMContext):
    await message.answer("Bu qism hali ishga tushmadi, sizga xabar beramiz")