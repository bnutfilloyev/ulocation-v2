from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.exceptions import TelegramBadRequest

from keyboards.location_kb import CityCD, CategoryCD, SubcategoryCD, LocationCD, CommentsCD
from keyboards.location_kb import cities_kb, categories_kb, subcategories_kb, locations_kb, image_navigation_kb
from keyboards.comment_kb import rating_kb, comment_action_kb
from structures.states import AddCommentState
from database import location_db, user_db
import io
import re


router = Router()

@router.message(F.text == "📍 Lokatsiyalar")
async def show_cities(message: types.Message, state: FSMContext):
    await state.clear()
    cities = await location_db.get_cities()
    
    if not cities:
        await message.answer("🏙️ Afsuski, hozircha shaharlar ro'yxati mavjud emas. Tez orada yangi shaharlar qo'shiladi va siz ular bo'ylab sayohat qilishingiz mumkin bo'ladi!", show_alert=True)
        return

    language = await user_db.get_user_language(user_id=message.from_user.id)
    await state.update_data(locale=language)

    btn = await cities_kb(cities, language)
    await message.answer("🏙️ Qaysi shahardagi qiziqarli joylar va mashhur manzillarni ko'rishni xohlaysiz? Quyidagi ro'yxatdan shaharni tanlang:", reply_markup=btn)


@router.callback_query(F.data == "back_to_cities")
async def back_to_cities_handler(callback: types.CallbackQuery, state: FSMContext):
    cities = await location_db.get_cities()
    update_date = await state.get_data()

    btn = await cities_kb(cities, update_date.get('locale'))
    await callback.message.edit_text("🏙️ Qaysi shahardagi joylarni ko'rishni xohlaysiz? Tanlang:", reply_markup=btn)
    await callback.answer()


@router.callback_query(CityCD.filter())
async def on_city_selected(callback: types.CallbackQuery, callback_data: CityCD, state: FSMContext):
    await state.update_data(city_id=callback_data.city_id)

    categories = await location_db.get_categories()

    if not categories:
        await callback.answer("📋 Bu shaharda hali kategoriyalar mavjud emas. Tez orada yangi kategoriyalar qo'shilib, shahar bo'ylab sayohat imkoniyati yaratiladi!", show_alert=True)
        return

    update_date = await state.get_data()
    btn = await categories_kb(categories, update_date.get('locale'))
    await callback.message.edit_text("📋 Qanday turdagi joylarni ko'rishni xohlaysiz? Qiziqishingizga mos kategoriyani tanlang:", reply_markup=btn)
    await callback.answer()


@router.callback_query(CategoryCD.filter())
async def on_category_selected(callback: types.CallbackQuery, callback_data: CategoryCD, state: FSMContext):
    category_id = callback_data.category_id
    await state.update_data(category_id=category_id)


    subcategories = await location_db.get_subcategories(category_id)

    if not subcategories:
        await callback.answer("🔍 Bu kategoriyada hozircha subkategoriyalar mavjud emas. Yaqin kunlarda yangi subkategoriyalar qo'shiladi va sizning tanlovingiz yanada kengayadi!", show_alert=True)
        return

    update_date = await state.get_data()
    btn = await subcategories_kb(subcategories, update_date.get('locale'))
    await callback.message.edit_text("🔍 Kategoriya ichidagi aniq yo'nalishni tanlang. Bu sizga ko'proq mos keluvchi joylarni topishga yordam beradi:", reply_markup=btn)
    await callback.answer()


# 4. Subkategoriya tanlanganda, shu subkategoriyaga tegishli lokatsiyalarni ko'rsatish
@router.callback_query(SubcategoryCD.filter())
async def on_subcategory_selected(callback: types.CallbackQuery, callback_data: SubcategoryCD, state: FSMContext):
    update_date = await state.get_data()
    city_id = update_date.get('city_id')
    category_id = update_date.get('category_id')
    subcategory_id = callback_data.subcategory_id
    locale = update_date.get('locale', 'uz')
    
    locations = await location_db.get_locations_by_param(
        city_id=city_id,
        category_id=category_id,
        subcategory_id=subcategory_id
    )
    
    if not locations:
        await callback.answer("📌 Bu subkategoriyada hozircha lokatsiyalar mavjud emas. Tez orada yangi va qiziqarli joylar ro'yxati bilan to'ldiriladi. Iltimos, boshqa subkategoriyani tanlang yoki keyinroq qayta tashrif buyuring!")
        return

    btn = await locations_kb(locations, locale)
    
    await callback.message.edit_text("📌 Quyidagi ro'yxatdan o'zingizga qiziq bo'lgan joyni tanlang. Har bir joy haqida batafsil ma'lumot, rasm va izohlarni ko'rishingiz mumkin:", reply_markup=btn)
    await callback.answer()


@router.callback_query(LocationCD.filter())
async def on_location_selected(callback: types.CallbackQuery, callback_data: LocationCD, state: FSMContext):
    location_id = callback_data.location_id
    update_date = await state.get_data()
    locale = update_date.get('locale', 'uz')
    
    # Store location_id in state
    await state.update_data(location_id=location_id)
    
    # Get location details
    loc = await location_db.get_location_by_id(location_id)
    
    if not loc:
        await callback.answer("❌ Kechirasiz, tanlangan lokatsiya ma'lumotlar bazasida topilmadi.")
        return
    
    # Get location name based on locale
    location_name = loc.get('name', {}).get(locale, loc.get('name', {}).get('uz', "Noma'lum"))
    
    # Get description if available
    description_raw = loc.get('description', {}).get(locale, loc.get('description', {}).get('uz', ""))
    # description = description_raw.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")    
    description = re.sub(r"<br\s*/?>", "\n", description_raw)

    # Format tags if available
    tags = loc.get('tags', [])
    tags_text = ""
    if tags:
        hashtags = [f"#{tag}" for tag in tags]
        tags_text = f"🏷️ {' '.join(hashtags)}\n"
    
    # Get price range
    price_range = loc.get('price_range', "Ma'lumot mavjud emas")
    
    # Get ratings
    average_rating = loc.get('average_rating', 0)
    rating_count = loc.get('rating_count', 0)
    rating_stars = "⭐" * int(average_rating) if average_rating else ""
    
    # Format main details
    details = f"🌟 <b>{location_name}</b> {rating_stars}\n\n"
    
    if description:
        details += f"{description}\n\n"
    
    details += f"💰 <b>Narx:</b> {price_range}\n"
    
    if tags_text:
        details += f"{tags_text}\n"
    
    details += f"⭐ <b>Reyting:</b> {average_rating} ({rating_count} ovoz)\n"
    
    # Add contact details if available
    if loc.get("phone"):
        details += f"📞 <b>Telefon:</b> {loc.get('phone')}\n"
    
    if loc.get("website"):
        details += f"🌐 <b>Veb-sayt:</b> {loc.get('website')}\n"
    
    # Create inline keyboard with buttons
    builder = InlineKeyboardBuilder()
    
    # Comments button
    builder.button(
        text="💬 Izohlarni ko'rish",
        callback_data=CommentsCD(location_id=location_id).pack()
    )
    
    # Images button - only if has images
    if loc.get("images") and len(loc.get("images")) > 0:
        builder.button(
            text="🖼 Rasmlarni ko'rish",
            callback_data=f"show_images:{location_id}:0"
        )
    
    # Location button (sends map)
    if loc.get("location") and loc.get("location").get("latitude") and loc.get("location").get("longitude"):
        builder.button(
            text="📍 Xaritada ko'rish",
            callback_data=f"send_location:{location_id}"
        )
    
    # Taxi button
    if loc.get("taxi_link"):
        builder.button(
            text="🚕 Taksi chaqirish",
            url=loc.get("taxi_link")
        )
    
    # Booking button
    if loc.get("booking_link"):
        builder.button(
            text="📅 Joy band qilish",
            url=loc.get("booking_link")
        )
    
    # Back button
    builder.button(
        text="⬅️ Orqaga",
        callback_data="back_to_cities"
    )
    
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(details, parse_mode="HTML", reply_markup=builder.as_markup())
    except TelegramBadRequest:
        await callback.message.answer(details, parse_mode="HTML", reply_markup=builder.as_markup())
    await callback.answer()


# Handler for showing images
@router.callback_query(F.data.startswith("show_images:"))
async def show_location_images(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    location_id = parts[1]
    current_index = int(parts[2])
    
    # Get all image IDs for this location
    image_ids = await location_db.get_location_images(location_id)
    
    if not image_ids or len(image_ids) == 0:
        await callback.answer("Bu joy uchun afsuski rasmlar mavjud emas. Tez orada rasmlar bilan to'ldiriladi va siz bu joyni vizual ko'rishingiz mumkin bo'ladi.", show_alert=True)
        return
    
    # Get the current image file metadata
    current_image_id = image_ids[current_index]
    image_file = await location_db.get_image_file(current_image_id)
    
    if not image_file:
        await callback.answer("Rasm ma'lumotlarini yuklab olishda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.", show_alert=True)
        return
    
    # Get the image binary data
    image_data = await location_db.get_image_data(current_image_id)
    
    if not image_data:
        await callback.answer("Rasm ma'lumotlarini yuklab olishda xatolik yuz berdi. Servidor bilan bog'lanishni tekshirib, qayta urinib ko'ring.", show_alert=True)
        return
    
    # Get location name for caption
    loc = await location_db.get_location_by_id(location_id)
    update_date = await state.get_data()
    locale = update_date.get('locale', 'uz')
    location_name = loc.get('name', {}).get(locale, loc.get('name', {}).get('uz', "Noma'lum"))
    
    # Create caption with image info
    filename = image_file.get('caption', '')
    width = image_file.get('width', 0)
    height = image_file.get('height', 0)
    caption = f"🖼 <b>{location_name}</b>\n"
    
    if filename:
        caption += f"📄 {filename}\n"
    
    if width and height:
        caption += f"📐 {width}x{height}\n"
    
    markup = await image_navigation_kb(location_id, current_index, len(image_ids))
    
    input_file = types.BufferedInputFile(
        file=image_data,
        filename=filename or f"image_{current_index}.jpg"
    )
    
    await callback.message.answer_photo(
        photo=input_file,
        caption=caption,
        parse_mode="HTML",
        reply_markup=markup
    )
    
    await callback.message.delete()
    await callback.answer()


# Comments handler with new comment button
@router.callback_query(CommentsCD.filter())
async def on_comments(callback: types.CallbackQuery, callback_data: CommentsCD, state: FSMContext):
    location_id = callback_data.location_id
    update_date = await state.get_data()
    locale = update_date.get('locale', 'uz')
    
    # Store location_id in state
    await state.update_data(location_id=location_id)
    
    # Get location for name and embedded comments
    loc = await location_db.get_location_by_id(location_id)
    
    if not loc:
        await callback.answer("Kechirasiz, bu joy ma'lumotlari topilmadi.")
        return
    
    # Get location name
    location_name = loc.get('name', {}).get(locale, loc.get('name', {}).get('uz', "Noma'lum"))
    
    # Get comments from the location document
    comments = loc.get('comments', [])
    
    # Build the comments text
    if comments:
        text = f"💬 <b>{location_name}</b> haqida tashrif buyuruvchilar fikrlari:\n\n"
        for i, comment in enumerate(comments, 1):
            user_name = comment.get("user_name", "Foydalanuvchi")
            comment_text = comment.get("text", "")
            rating = comment.get("rating", 0)
            rating_stars = "⭐" * int(rating)
            created_at = comment.get("created_at", "")
            date_str = ""
            
            # Format date if available
            if created_at:
                if hasattr(created_at, 'strftime'):
                    date_str = f" • {created_at.strftime('%d.%m.%Y')}"
                else:
                    date_str = f" • {created_at}"
                    
            text += f"{i}. <b>{user_name}</b>{date_str}\n"
            text += f"{rating_stars} {rating}/5\n"
            text += f"{comment_text}\n\n"
    else:
        text = f"📢 <b>{location_name}</b> haqida hali izohlar qoldirilmagan. Birinchi bo'lib o'z fikringizni qoldiring!"
    
    # Create buttons
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Yangi izoh qoldirish", callback_data=f"new_comment:{location_id}")
    builder.button(text="⬅️ Orqaga", callback_data=f"back_to_location_details:{location_id}")
    builder.adjust(1)
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=builder.as_markup())
    await callback.answer()


# New comment handler - start process
@router.callback_query(F.data.startswith("new_comment:"))
async def start_new_comment(callback: types.CallbackQuery, state: FSMContext):
    location_id = callback.data.split(":")[1]
    
    # Store location_id in state
    await state.update_data(location_id=location_id)
    
    # Set state to waiting for rating
    await state.set_state(AddCommentState.waiting_for_rating)
    
    # Show rating selection keyboard
    await callback.message.edit_text(
        "🌟 Iltimos, bu joyga o'z bahongizni bering (1-5 yulduz):\n\n"
        "1⭐ - Mutlaqo yoqmadi\n"
        "2⭐ - Qoniqarsiz\n"
        "3⭐ - O'rtacha\n"
        "4⭐ - Yaxshi\n"
        "5⭐ - Ajoyib",
        reply_markup=rating_kb()
    )
    await callback.answer()


# Handle rating selection
@router.callback_query(F.data.startswith("rating:"), AddCommentState.waiting_for_rating)
async def process_rating(callback: types.CallbackQuery, state: FSMContext):
    # Extract rating value
    rating = int(callback.data.split(":")[1])
    
    # Store rating in state
    await state.update_data(rating=rating)
    
    # Move to next state - waiting for comment text
    await state.set_state(AddCommentState.waiting_for_comment_text)
    
    # Create cancel button
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Bekor qilish", callback_data="cancel_comment")
    
    # Ask for comment text
    await callback.message.edit_text(
        f"Sizning bahoyingiz: {'⭐' * rating} ({rating}/5)\n\n"
        f"Endi fikringizni yozing. Bu joy haqida boshqalarga nimani aytishni istaysiz? "
        f"Nimasi yaxshi, nimasi yoqmadi, nimaga e'tibor berish kerak va h.k.:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


# Handle comment text input
@router.message(AddCommentState.waiting_for_comment_text)
async def process_comment_text(message: types.Message, state: FSMContext):
    # Get comment text
    comment_text = message.text
    
    if not comment_text or len(comment_text) < 2:
        await message.answer("Iltimos, kamida 2 ta belgi kiriting. Izohingiz yanada ko'proq ma'lumot bersa, boshqalarga yordam bo'ladi.")
        return
    
    # Get state data
    state_data = await state.get_data()
    location_id = state_data.get("location_id")
    rating = state_data.get("rating")
    
    # Get user info
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    
    # Save comment directly to location's comments array
    success = await location_db.add_comment(
        location_id=location_id,
        user_id=user_id,
        user_name=user_name,
        rating=rating,
        comment_text=comment_text
    )
    
    # Clear state
    await state.clear()
    
    if success:
        # Thank user for comment
        await message.answer(
            f"Rahmat! Sizning {'⭐' * rating} ({rating}/5) bahoingiz va fikringiz muvaffaqiyatli qabul qilindi. "
            f"Sizning izohingiz boshqalarga bu joy haqida to'g'ri tasavvur hosil qilishlariga yordam beradi.",
            reply_markup=comment_action_kb(location_id)
        )
    else:
        # Inform about error
        await message.answer(
            "Kechirasiz, izohingizni saqlashda texnik xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring yoki administrator bilan bog'laning.",
            reply_markup=comment_action_kb(location_id)
        )


# Cancel comment
@router.callback_query(F.data == "cancel_comment")
async def cancel_comment(callback: types.CallbackQuery, state: FSMContext):
    # Get location_id from state
    state_data = await state.get_data()
    location_id = state_data.get("location_id")
    
    # Clear state
    await state.clear()
    
    # Return to location details
    fake_callback_data = LocationCD(location_id=location_id)
    await on_location_selected(callback, fake_callback_data, state)
    await callback.answer("Izoh qoldirish jarayoni bekor qilindi. Siz istagan vaqtda qayta izoh qoldirishingiz mumkin.")


# Show all comments
@router.callback_query(F.data.startswith("show_all_comments:"))
async def show_all_comments(callback: types.CallbackQuery, state: FSMContext):
    location_id = callback.data.split(":")[1]
    
    # Reuse existing comments handler
    fake_callback_data = CommentsCD(location_id=location_id)
    await on_comments(callback, fake_callback_data, state)


# Add a handler for sending location on map
@router.callback_query(F.data.startswith("send_location:"))
async def send_location_on_map(callback: types.CallbackQuery, state: FSMContext):
    location_id = callback.data.split(":")[1]
    
    # Get location details
    loc = await location_db.get_location_by_id(location_id)
    
    if not loc or not loc.get("location"):
        await callback.answer("Kechirasiz, bu joy uchun aniq manzil ma'lumotlari kiritilmagan. Administrator bilan bog'laning yoki boshqa joylarni ko'rib chiqing.")
        return
    
    # Get location coordinates
    latitude = loc.get("location").get("latitude")
    longitude = loc.get("location").get("longitude")
    
    if not latitude or not longitude:
        await callback.answer("Kechirasiz, bu joy uchun aniq koordinatalar topilmadi. Manzil ma'lumotlari to'liq kiritilmaganga o'xshaydi.")
        return
    
    update_date = await state.get_data()
    locale = update_date.get('locale', 'uz')
    
    # Get location name
    location_name = loc.get('name', {}).get(locale, loc.get('name', {}).get('uz', "Noma'lum"))
    
    # Send location
    await callback.message.answer_location(
        latitude=latitude,
        longitude=longitude
    )
    
    # Create back button
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Joyga qaytish",
        callback_data=f"back_to_location_details:{location_id}"
    )
    
    await callback.message.answer(
        f"📍 <b>{location_name}</b> joylashuvi. Xaritada ko'rsatilgan joyga tashrif buyurishingiz mumkin. Manzil bo'yicha qo'shimcha savol va takliflar bo'lsa, administratorga murojaat qiling.", 
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# Handler for going back to location details
@router.callback_query(F.data.startswith("back_to_location_details:"))
async def back_to_location_details(callback: types.CallbackQuery, state: FSMContext):
    location_id = callback.data.split(":")[1]
    
    # Reuse the existing location selection handler with a fake callback_data
    fake_callback_data = LocationCD(location_id=location_id)
    await on_location_selected(callback, fake_callback_data, state)

# Comments handler with improved display
@router.callback_query(CommentsCD.filter())
async def on_comments(callback: types.CallbackQuery, callback_data: CommentsCD, state: FSMContext):
    location_id = callback_data.location_id
    update_date = await state.get_data()
    locale = update_date.get('locale', 'uz')
    
    # Get location for name and existing comments
    loc = await location_db.get_location_by_id(location_id)
    
    if not loc:
        await callback.answer("Kechirasiz, bu joy ma'lumotlari topilmadi.", show_alert=True)
        return
    
    # Get location name
    location_name = loc.get('name', {}).get(locale, loc.get('name', {}).get('uz', "Noma'lum"))
    
    # Get comments from the location document or from separate collection
    comments = []
    if 'comments' in loc and loc.get('comments'):
        # If comments are stored directly in the location document
        comments = loc.get('comments')
    else:
        # If comments are stored in a separate collection
        comments = await location_db.get_comments_by_location(location_id)
    
    # Build the comments text
    if comments:
        text = f"💬 <b>{location_name}</b> haqida tashrif buyuruvchilar fikrlari va baholari:\n\n"
        for i, comment in enumerate(comments, 1):
            user_name = comment.get("user_name", "Foydalanuvchi")
            comment_text = comment.get("text", comment.get("comment", ""))
            rating = comment.get("rating", 0)
            rating_stars = "⭐" * int(rating)
            date = comment.get("date", "")
            date_str = f" • {date}" if date else ""
            
            text += f"{i}. <b>{user_name}</b>{date_str}\n"
            text += f"{rating_stars} {rating}/5\n"
            text += f"{comment_text}\n\n"
    else:
        text = f"📢 <b>{location_name}</b> haqida hali izohlar qoldirilmagan. Ushbu joyga tashrif buyurgan bo'lsangiz, birinchi bo'lib o'z fikringiz va taassurotlaringizni qoldiring!"
    
    # Create buttons
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Yangi izoh qoldirish", callback_data=f"new_comment:{location_id}")
    builder.button(text="⬅️ Orqaga", callback_data=f"back_to_location_details:{location_id}")
    builder.adjust(1)
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=builder.as_markup())
    await callback.answer()
