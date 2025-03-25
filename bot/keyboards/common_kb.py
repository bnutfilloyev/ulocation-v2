from aiogram.filters.callback_data import CallbackData
from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)
from aiogram.utils.keyboard import InlineKeyboardBuilder

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
            KeyboardButton(text="💥 Aksiyalar"),
            KeyboardButton(text="📍 Lokatsiyalar"),
        ],
        [KeyboardButton(text="🎯 Referral")],
    ],
    resize_keyboard=True,
    input_field_placeholder=None,
)
