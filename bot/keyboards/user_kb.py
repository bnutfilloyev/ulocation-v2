from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


class UserPromoCD(CallbackData, prefix="promo"):
    promo_id: str


async def promotions_kb(promotions: list):
    builder = InlineKeyboardBuilder()
    for promo in promotions:
        builder.button(
            text=promo["name"], callback_data=UserPromoCD(promo_id=str(promo["_id"]))
        )
    return builder.adjust(1).as_markup()
