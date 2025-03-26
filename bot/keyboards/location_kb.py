from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CityCD(CallbackData, prefix="city"):
    city_id: str

class CategoryCD(CallbackData, prefix="category"):
    category_id: str

class SubcategoryCD(CallbackData, prefix="subcategory"):
    subcategory_id: str

class LocationCD(CallbackData, prefix="location"):
    location_id: str

class CommentsCD(CallbackData, prefix="comments"):
    location_id: str


async def cities_kb(cities: list, locale: str) -> str:
    builder = InlineKeyboardBuilder()
    
    for city in cities:
        city_id = str(city.get('_id'))
        city_name = city.get('name').get(locale)
        
        builder.add(
            InlineKeyboardButton(
                text=city_name,
                callback_data=CityCD(city_id=city_id).pack()
            )
        )
    
    builder.adjust(3)
    
    return builder.as_markup()


async def categories_kb(categories: list, locale: str):
    builder = InlineKeyboardBuilder()

    for category in categories:
        category_id = str(category.get("_id"))
        category_name = category.get('name').get(locale)

        builder.add(InlineKeyboardButton(text=category_name, callback_data=CategoryCD(category_id=category_id).pack()))

    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="back_to_cities"))

    return builder.as_markup()


async def subcategories_kb(subcategories: list, locale: str):
    builder = InlineKeyboardBuilder()
    
    for subcategory in subcategories:
        subcategory_id = str(subcategory.get("_id"))
        subcategory_name = subcategory.get('name').get(locale)
        
        builder.add(
            InlineKeyboardButton(
                text=subcategory_name,
                callback_data=SubcategoryCD(subcategory_id=subcategory_id).pack()
            )
        )
    
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data=f"back_to_cities"))
    
    return builder.as_markup()


async def locations_kb(locations: list, locale: str):
    """Create keyboard with location buttons"""
    builder = InlineKeyboardBuilder()
    
    for location in locations:
        location_id = str(location.get('_id'))
        location_name = location.get('name').get(locale)
        
        builder.add(
            InlineKeyboardButton(
                text=location_name,
                callback_data=LocationCD(location_id=location_id).pack()
            )
        )
    
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data=f"back_to_cities"))
    
    return builder.as_markup()

# New function for image navigation
async def image_navigation_kb(location_id: str, current_index: int, total_images: int):
    """Create keyboard for navigating through location images"""
    builder = InlineKeyboardBuilder()
    
    # Add navigation buttons based on current position
    if total_images > 1:
        # Add prev button if not at first image
        if current_index > 0:
            builder.button(text="⬅️", callback_data=f"image:{location_id}:{current_index-1}")
        
        # Show current position
        builder.button(text=f"{current_index+1}/{total_images}", callback_data="do_nothing")
        
        # Add next button if not at last image
        if current_index < total_images - 1:
            builder.button(text="➡️", callback_data=f"image:{location_id}:{current_index+1}")
    
    # Add button to return to location details
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"back_to_location_details:{location_id}"))
    
    return builder.as_markup()

