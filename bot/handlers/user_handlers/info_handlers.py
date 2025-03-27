from aiogram import F, Router, types

router = Router()

@router.message(F.text.in_(["📞 Aloqa", "📞 Контакт", "📞 Contact"]))
async def handle_contact(message: types.Message):
    """Handler for contact information button"""
    contact_text = (
        "<b>Aloqa uchun ma'lumotlar:</b>\n"
        "Agar sizda savollar, takliflar yoki hamkorlik bo'yicha murojaatlar bo'lsa, biz bilan bog'laning:\n\n"
        "📞 Telefon: <code>+998 90 636 63 13</code>\n"
        "✈️ Telegram: @smmproceo\n\n"
        "Biz har doim sizga yordam berishga tayyormiz!\n"
        "<b>Ulocation — joyni bilgan yutadi!</b>"
    )
    
    await message.answer(contact_text)

@router.message(F.text.in_(["💬 FAQ", "💬 ЧЗВ"]))
async def handle_faq(message: types.Message):
    """Handler for FAQ button"""
    faq_text = (
        "<b>FAQ — Tez-tez so'raladigan savollar</b>\n\n"
        "<b>1. Botdan qanday foydalanaman?</b>\n"
        "Botdan foydalanish uchun avval 15 000 so'm to'lab obuna bo'lasiz. So'ngra sizga barcha chegirmalar, "
        "bepul xizmatlar va lokatsiyalar ochiladi.\n\n"
        
        "<b>2. Obuna qancha muddatga amal qiladi?</b>\n"
        "Obuna muddati 1 oy. Har oy qayta to'lov qilgan holda barcha imkoniyatlardan foydalanishda davom etasiz.\n\n"
        
        "<b>3. Qanday chegirmalar beriladi?</b>\n"
        "Bizning hamkorlarimiz orqali siz:\n"
        "— kafelarda bepul mahsulotlar\n"
        "— salon va xizmatlarda chegirmalar\n"
        "— dorixona va boshqa joylarda bonusli xizmatlarga ega bo'lasiz.\n"
        "Takliflar doimiy yangilanib boradi.\n\n"
        
        "<b>4. Qanday lokatsiyalar haqida ma'lumot olaman?</b>\n"
        "O'zbekistondagi qiziqarli joylar, maskanlar, maxfiy lokatsiyalar, tavsiyalar va faqat ichki "
        "auditoriyaga mo'ljallangan faktlar sizga taqdim etiladi.\n\n"
        
        "<b>5. To'lovni qanday amalga oshiraman?</b>\n"
        "\"To'lov qilish\" tugmasi orqali bot ichida to'lovni amalga oshirishingiz mumkin. "
        "To'lovdan so'ng barcha imkoniyatlar siz uchun faollashadi.\n\n"
        
        "<b>6. Muammo yuz bersa kimga murojaat qilaman?</b>\n"
        "Agar biron muammo yoki savol bo'lsa:\n"
        "📞 <code>+998 90 636 63 13</code>\n"
        "✈️ Telegram: @smmproceo\n\n"
        
        "<b>7. Chegirmalar faqat bir martalikmi?</b>\n"
        "Ha, har bir taklif faqat bir marta ishlatiladi, ammo siz oy davomida istalgan taklifdan foydalana olasiz."
    )
    
    await message.answer(faq_text)
