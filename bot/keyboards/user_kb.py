from aiogram.filters.callback_data import CallbackData
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


class LanguageCD(CallbackData, prefix="language"):
    lang: str


def language_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha", callback_data=LanguageCD(lang="uz"))
    builder.button(text="🇷🇺 Русский", callback_data=LanguageCD(lang="ru"))
    builder.button(text="🇺🇸 English", callback_data=LanguageCD(lang="en"))
    return builder.adjust(2).as_markup()

