from aiogram.filters.callback_data import CallbackData
from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menus_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Partner sozlamalari", callback_data="admin_partner_settings")
    return builder.as_markup()


def admin_partner_menus_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Qo'shish", callback_data="admin_partner_add")
    builder.button(text="O'chirish", callback_data="admin_partner_delete")
    return builder.as_markup()
