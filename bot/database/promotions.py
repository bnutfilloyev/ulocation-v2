import random
import string
from datetime import datetime

from bson.objectid import ObjectId

from .base import MongoDB


class PromotionDB(MongoDB):
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
    
    async def get_image_data(self, file_id: str):
        """Get binary image data from chunks collection"""
        cursor = self.db.promotion_images.chunks.find({"files_id": ObjectId(file_id)}).sort("n", 1)
        
        if not cursor:
            return None
        
        data = bytearray()
        async for chunk in cursor:
            if chunk.get("data"):
                # Extract binary data from the chunk
                chunk_data = chunk.get("data")
                if isinstance(chunk_data, dict) and "$binary" in chunk_data:
                    # Handle MongoDB binary format
                    import base64
                    binary_data = base64.b64decode(chunk_data["$binary"]["base64"])
                    data.extend(binary_data)
                else:
                    # Handle regular binary data
                    data.extend(chunk_data)
        
        return bytes(data) if data else None
    

    async def get_promotion_image(self, image_id: str):
        image_file = await self.db.promotion_images.files.find_one(
            {"_id": ObjectId(image_id)}
        )
        if not image_file:
            return None, None
        
        image_data = await self.get_image_data(image_id)
        
        return image_file, image_data
        
    

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
        Foydalanuvchi uchun ushbu aksiya bo'yicha promo kodni olish.
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
