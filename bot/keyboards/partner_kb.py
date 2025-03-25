from aiogram.filters.callback_data import CallbackData
from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)
from aiogram.utils.keyboard import InlineKeyboardBuilder


class PartnerCD(CallbackData, prefix="partner"):
    action: str
    partner_login: str


async def get_partner_kb(partners: list):
    builder = InlineKeyboardBuilder()
    for partner in partners:
        button_text = partner.get("partner_name") or partner.get("partner_login")
        callback_data = PartnerCD(
            action="delete", partner_login=partner.get("partner_login")
        ).pack()
        builder.button(text=button_text, callback_data=callback_data)
    return builder.as_markup()


class PartnerMenuCD(CallbackData, prefix="partnermenu"):
    action: str
    partner_id: str


async def partner_menu_kb(partner_id: str):
    builder = InlineKeyboardBuilder()
    partner_id = str(partner_id)

    builder.button(
        text="➕ Aksiya qo‘shish",
        callback_data=PartnerMenuCD(
            action="add_promotion", partner_id=partner_id
        ).pack(),
    )
    builder.button(
        text="❌ Aksiyani tugatish",
        callback_data=PartnerMenuCD(
            action="finish_promotion", partner_id=partner_id
        ).pack(),
    )
    builder.button(
        text="📊 Hisobotlar",
        callback_data=PartnerMenuCD(action="reports", partner_id=partner_id).pack(),
    )
    builder.button(
        text="🔍 Promokodni tekshirish",
        callback_data=PartnerMenuCD(
            action="check_promo_code", partner_id=partner_id
        ).pack(),
    )

    builder.adjust(1)
    return builder.as_markup()


class PartnerPromotionCD(CallbackData, prefix="partner_promotion"):
    promotion_id: str


async def get_partner_promotions_kb(promotions: list):
    builder = InlineKeyboardBuilder()
    for promo in promotions:
        button_text = promo.get("name")
        callback_data = PartnerPromotionCD(promotion_id=str(promo.get("_id"))).pack()
        builder.button(text=button_text, callback_data=callback_data)

    return builder.adjust(1).as_markup()
