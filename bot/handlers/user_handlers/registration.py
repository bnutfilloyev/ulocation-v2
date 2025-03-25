from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from configuration import conf
from database import user_db
from keyboards.common_kb import agreement_kb, contact_kb, main_menu_kb
from keyboards.user_kb import LanguageCD
from structures.states import RegState
from utils.user_check import check_user_stepwise
from keyboards.common_kb import link_kb
from aiogram.types import FSInputFile


router = Router()


@router.callback_query(LanguageCD.filter())
async def set_language(query: types.CallbackQuery, callback_data: LanguageCD, state: FSMContext):   
    await query.message.delete()
    await state.update_data(locale=callback_data.lang)
    await user_db.user_update(user_id=query.from_user.id, data={"language": callback_data.lang})
    
    if not await check_user_stepwise(query.message, state):  
        return
    
    text = (
        "😊 <b>Sizni yana ko‘rishdan xursandmiz!</b>\n\n"
        "📌 <b>Botdan foydalanish uchun quyidagi tugmalardan foydalaning:</b>"
    )
    await query.message.answer(text=text, reply_markup=main_menu_kb)
    

@router.message(RegState.fullname, ~F.text.startswith("/"))
async def input_firstname(message: types.Message, state: FSMContext):
    await state.update_data(input_fullname=message.text)
    await user_db.user_update(user_id=message.from_user.id, data={"input_fullname": message.text})
   
    if not await check_user_stepwise(message, state):
        return
    
    text = (
        "😊 <b>Sizni yana ko‘rishdan xursandmiz!</b>\n\n"
        "📌 <b>Botdan foydalanish uchun quyidagi tugmalardan foydalaning:</b>"
    )
    await message.answer(text=text, reply_markup=main_menu_kb)




@router.message(RegState.phone_number, ~F.text.startswith("/") | F.text | F.contact)
async def input_phone(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text
    else:
        return await message.answer(
            "❌ <b>Noto‘g‘ri format!</b> Iltimos, telefon raqamingizni to‘g‘ri kiriting.",
        )

    await state.update_data(input_phone=phone)
    await user_db.user_update(user_id=message.from_user.id, data={"input_phone": phone})

    if not await check_user_stepwise(message, state):
        return
    
    text = (
        "😊 <b>Sizni yana ko‘rishdan xursandmiz!</b>\n\n"
        "📌 <b>Botdan foydalanish uchun quyidagi tugmalardan foydalaning:</b>"
    )
    await message.answer(text=text, reply_markup=main_menu_kb)



@router.callback_query(F.data.startswith("agreement:"))
async def process_agreement(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_reply_markup(reply_markup=None)
    await query.answer("✅ Oferta shartlari tasdiqlandi!")
    await user_db.user_update(user_id=query.from_user.id, data={"agreement": True})

    if not await check_user_stepwise(query.message, state):
        return
    
    text = (
        "😊 <b>Sizni yana ko‘rishdan xursandmiz!</b>\n\n"
        "📌 <b>Botdan foydalanish uchun quyidagi tugmalardan foydalaning:</b>"
    )
    await query.message.answer(text=text, reply_markup=main_menu_kb)
