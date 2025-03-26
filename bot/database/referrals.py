from datetime import datetime
from dateutil.relativedelta import relativedelta

from .base import MongoDB


class ReferralDB(MongoDB):
    async def add_referral(self, user_id: str, referrer_id: str):
        user_id = str(user_id)
        referrer_id = str(referrer_id)

        if user_id == referrer_id:
            return False

        user_info = await self.db.users.find_one({"user_id": user_id})
        
        if user_info and not user_info.get("referrer_id"):
            await self.db.users.update_one(
                {"user_id": user_id},
                {"$set": {"referrer_id": referrer_id}}
            )
            return True
        return False

    async def process_referral_payment(self, user_id: str):
        user_id = str(user_id)
        user = await self.db.users.find_one({"user_id": user_id})

        if user and user.get("referrer_id"):
            referrer_id = user["referrer_id"]

            existing_payment = await self.db.referral_payments.find_one({
                "referral_user_id": user_id,
                "payment_status": "paid"
            })

            if existing_payment:
                return False

            await self.db.referral_payments.insert_one({
                "referrer_id": referrer_id,
                "referral_user_id": user_id,
                "payment_status": "paid",
                "payment_date": datetime.now()
            })
            
            referrer = await self.db.users.find_one({"user_id": referrer_id})
            new_count = referrer.get("referral_count", 0) + 1
            new_bonus = referrer.get("referral_bonus_months", 0)
            
            if referrer.get("is_sponsor"):
                new_count = referrer.get("referral_count", 0) + 1
                return await self.db.users.update_one(
                    {"user_id": referrer_id},
                    {"$set": {"referral_count": new_count}}
                )


            if new_count % 5 == 0:
                new_bonus += 1
                expiry_date = referrer.get("expiry_date")
                if expiry_date:
                    new_expiry = expiry_date + relativedelta(months=1)
                    await self.db.users.update_one(
                        {"user_id": referrer_id},
                        {"$set": {"expiry_date": new_expiry}}
                    )

            await self.db.users.update_one(
                {"user_id": referrer_id},
                {"$set": {"referral_count": new_count, "referral_bonus_months": new_bonus}}
            )
            return True

        return False

    async def get_referrer(self, user_id: str) -> str:
        user = await self.db.users.find_one({"user_id": str(user_id)})
        return user.get("referrer_id") if user else None
