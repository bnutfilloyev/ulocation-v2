from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

remove_kb = ReplyKeyboardRemove()


skip_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🚫 O'tkazib yuborish")]],
    resize_keyboard=True,
    input_field_placeholder="Agar rasmsiz davom ettirmoqchi bo'lsangiz, tugmani bosing",
)


contact_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Telefon raqamingizni kiriting yoki tugmani bosing",
)


main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💲 1DOLLARSCLUB"),
            KeyboardButton(text="📍 Lokatsiyalar"),
        ],
        [
            KeyboardButton(text="🎯 Referral"),
            KeyboardButton(text="🤝 Hamkor bo'lish"),
        ],
        [
            KeyboardButton(text="📞 Aloqa"),
            KeyboardButton(text="💬 FAQ")
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder=None,
)


link_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Aloqa"), KeyboardButton(text="💬 FAQ")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# Faqat "Roziman" tugmasini yaratish
def agreement_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Roziman", callback_data="agreement:accept")
    
    return builder.as_markup()


