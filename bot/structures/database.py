from urllib.parse import quote_plus
from datetime import datetime
import random
import string

from bson.objectid import ObjectId
from configuration import conf
from motor import motor_asyncio


class MongoDB:
    def __init__(self):
        if conf.bot.debug:
            self.client = motor_asyncio.AsyncIOMotorClient(host="localhost", port=27017)
        else:
            self.client = motor_asyncio.AsyncIOMotorClient(
                host=conf.db.host,
                port=conf.db.port,
                username=quote_plus(conf.db.username),
                password=quote_plus(conf.db.password),
            )
        self.db = self.client[conf.db.database]

    async def user_update(self, user_id, data=None):
        user_id = str(user_id)
        user_info = await self.db.users.find_one({"user_id": user_id})

        if user_info is None:
            await self.db.users.insert_one({"user_id": user_id})
            return await self.user_update(user_id, data)

        if data:
            await self.db.users.update_one(
                {"user_id": user_id}, {"$set": data}, upsert=True
            )
            return await self.user_update(user_id)
        return user_info

    async def users_list(self):
        return await self.db.users.find().to_list(length=None)

    # --- Partner bilan bog'liq funksiyalar ---
    async def get_partner(self, login: str):
        return await self.db.partners.find_one({"partner_login": login})

    async def get_parners(self):
        return await self.db.partners.find().to_list(length=None)

    async def check_partner_credentials(self, login: str, password: str):
        partner = await self.get_partner(login)
        if partner and partner.get("partner_password") == password:
            return partner
        return None

    async def add_partner(self, partner_data: dict) -> bool:
        partner_login = partner_data.get("partner_login")
        if await self.get_partner(partner_login):
            return False
        result = await self.db.partners.insert_one(partner_data)
        return result.inserted_id is not None

    # --- Aksiyalar bilan bog'liq funksiyalar ---
    async def add_promotion(
        self,
        partner_id: str,
        name: str,
        description: str,
        category: str,
        image: str = None,
    ):
        new_promo = {
            "partner_id": ObjectId(partner_id),
            "name": name,
            "description": description,
            "category": category,
            "image": image,  # Aksiya uchun rasm (ixtiyoriy)
            "created_at": datetime.now(),
            "is_active": True,  # Aksiya faolligini belgilash
        }
        result = await self.db.promotions.insert_one(new_promo)
        return result.inserted_id if result.acknowledged else None

    async def finish_promotion(self, promotion_id: str):
        result = await self.db.promotions.update_one(
            {"_id": ObjectId(promotion_id)}, {"$set": {"is_active": False}}
        )
        return result.modified_count > 0  # True yoki False qaytaradi

    async def get_active_promotions(self, partner_id: str = None):
        if partner_id is None:
            return await self.db.promotions.find({"is_active": True}).to_list(
                length=None
            )

        return await self.db.promotions.find(
            {"partner_id": ObjectId(partner_id), "is_active": True}
        ).to_list(length=None)

    async def get_promotion(self, promotion_id: str):
        promotion_info = await self.db.promotions.find_one(
            {"_id": ObjectId(promotion_id)}
        )
        return promotion_info

    async def generate_user_promo_code(self, user_id: str, promotion_id: str):
        existing_promo = await self.db.user_promo_codes.find_one(
            {"user_id": user_id, "promotion_id": ObjectId(promotion_id)}
        )

        if existing_promo:
            if existing_promo.get("used"):
                return None
            
            return existing_promo["code"]

        new_code = self.generate_promo_code()
        promo_entry = {
            "user_id": user_id,
            "promotion_id": ObjectId(promotion_id),
            "code": new_code,
            "generated_at": datetime.now(),
            "used": False,
        }
        await self.db.user_promo_codes.insert_one(promo_entry)
        return new_code

    async def get_user_promo_code(self, user_id: str, promotion_id: str):
        """
        Foydalanuvchi uchun ushbu aksiya bo‘yicha promo kodni olish.
        """
        return await self.db.user_promo_codes.find_one(
            {"user_id": user_id, "promotion_id": ObjectId(promotion_id)}
        )

    async def mark_promo_code_as_used(self, promo_code: str):
        """
        Promo kodni ishlatilgan deb belgilash.
        """
        result = await self.db.user_promo_codes.update_one(
            {"code": promo_code}, {"$set": {"used": True, "used_at": datetime.now()}}
        )
        return result.modified_count > 0
    
    async def check_promo_code(self, promo_code: str):
        result = await self.db.user_promo_codes.find_one({"code": promo_code})
        
        if result:
            promotion_id = result["promotion_id"]
            promotion = await self.get_promotion(promotion_id)
            result["promotion"] = promotion

        return result

    def generate_promo_code(self, length=8):
        """
        Tasodifiy alfanumerik promo kod yaratish.
        """
        letters_and_digits = string.ascii_uppercase + string.digits
        return "".join(random.choices(letters_and_digits, k=length))
    



db = MongoDB()
