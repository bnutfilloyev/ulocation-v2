import time
from aiogram import Bot, Router, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from database import user_db
from keyboards.common_kb import main_menu_kb, remove_kb
from utils.user_check import check_user_referral, check_user_stepwise
from structures.states import RegState, PaymentState
from utils.click_payment import click_payment_instance
from utils.user_check import check_user_stepwise

router = Router()


@router.message(PaymentState.waiting_for_card_number)
async def process_card_number(message: types.Message, state: FSMContext):
    card_number = ''.join(message.text.split())
    print(f"Card number: {card_number}")

    if not card_number.isdigit() or len(card_number) != 16:
        await message.answer(
            _("❌ <b>Noto'g'ri karta raqami!</b>\n\n"
              "🔹 Iltimos, 16 raqamli karta raqamini kiriting."),
            reply_markup=remove_kb
        )
        return

    await state.update_data(card_number=card_number)
    await message.answer(
        _("✅ Karta raqami qabul qilindi. Endi karta amal qilish muddatini kiriting."),
        reply_markup=remove_kb
    )
    await state.set_state(PaymentState.waiting_for_card_expiration)

@router.message(PaymentState.waiting_for_card_expiration)
async def process_card_expiration(message: types.Message, state: FSMContext):
    card_expiration = message.text.strip()

    if not card_expiration or len(card_expiration) != 4 or card_expiration[2] != '/':
        await message.answer(
            _("❌ <b>Noto'g'ri karta amal qilish muddati!</b>\n\n"
              "🔹 Iltimos, MM/YY formatida amal qilish muddatini kiriting."),
            reply_markup=remove_kb
        )
        return
    
    state_data = await state.get_data()
    card_number = state_data.get('card_number')

    response = await click_payment_instance.create_card_token(
        card_number=card_number,
        expiration_date=card_expiration
    )
    print(f"Card token response: {response}")
    if response.get("error"):
        await message.answer(
            _("❌ <b>Karta tokenini yaratishda xato yuz berdi!</b>\n\n"
              "🔹 Iltimos, qayta urinib ko'ring."),
            reply_markup=remove_kb
        )
        return
    card_token = response.get("card_token")
    await state.update_data(card_token=card_token)
    await message.answer(
        _("✅ Karta amal qilish muddati qabul qilindi. Endi SMS kodini kiriting."),
        reply_markup=remove_kb
    )
    await state.set_state(PaymentState.waiting_for_sms_code)

@router.message(PaymentState.waiting_for_sms_code)
async def process_sms_code(message: types.Message, state: FSMContext):
    sms_code = message.text.strip()

    if not sms_code.isdigit() or len(sms_code) != 6:
        await message.answer(
            _("❌ <b>Noto'g'ri SMS kod!</b>\n\n"
              "🔹 Iltimos, 6 raqamli SMS kodini kiriting."),
            reply_markup=remove_kb
        )
        return

    state_data = await state.get_data()
    card_token = state_data.get('card_token')

    response = await click_payment_instance.verify_card_token(
        sms_code=sms_code,
        card_token=card_token
    )
    if response.get("error"):
        await message.answer(
            _("❌ <b>SMS kodni tasdiqlashda xato yuz berdi!</b>\n\n"
              "🔹 Iltimos, qayta urinib ko'ring."),
            reply_markup=remove_kb
        )
        return

    await message.answer(
        _("✅ SMS kod tasdiqlandi. To'lov amalga oshirilmoqda..."),
        reply_markup=remove_kb
    )

    amount = 15_000_00  # 15,000 UZS
    transaction_parameter = str(message.from_user.id + time.time())
    response = await click_payment_instance.payment_with_token(
        card_token=card_token,
        amount=amount,
        transaction_parameter=transaction_parameter
    )
    if response.get("error"):
        await message.answer(
            _("❌ <b>To'lovda xato yuz berdi!</b>\n\n"
              "🔹 Iltimos, qayta urinib ko'ring."),
            reply_markup=remove_kb
        )
        return
    await message.answer(
        _("✅ To'lov muvaffaqiyatli amalga oshirildi!"),
        reply_markup=main_menu_kb()
    )
    await state.clear()
    await check_user_stepwise(message=message, state=state)