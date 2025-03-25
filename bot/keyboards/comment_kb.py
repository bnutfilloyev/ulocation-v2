from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def rating_kb():
    """Create rating keyboard for comments"""
    builder = InlineKeyboardBuilder()
    
    # Add buttons for 1-5 stars
    for i in range(1, 6):
        stars = "⭐" * i
        builder.button(text=f"{stars} ({i})", callback_data=f"rating:{i}")
    
    # Add cancel button
    builder.button(text="❌ Izoh qoldirishni bekor qilish", callback_data="cancel_comment")
    
    builder.adjust(1, 1)  # 5 buttons in first row, 1 in second
    
    return builder.as_markup()


def comment_action_kb(location_id: str):
    """Keyboard after comment is submitted"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🔙 Joy haqida batafsil ma'lumotlarga qaytish", callback_data=f"back_to_location_details:{location_id}")
    builder.button(text="💬 Barcha tashrif buyuruvchilar izohlarini ko'rish", callback_data=f"show_all_comments:{location_id}")
    
    builder.adjust(1)
    
    return builder.as_markup()
