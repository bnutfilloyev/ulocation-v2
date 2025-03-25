from .base import MongoDB


class UserDB(MongoDB):
    async def user_update(self, user_id, data=None):
        user_id = str(user_id)
        user_info = await self.db.users.find_one({"user_id": user_id})

        if user_info is None:
            await self.db.users.insert_one({"user_id": user_id})
            return await self.user_update(user_id, data)

        if data:
            await self.db.users.update_one({"user_id": user_id}, {"$set": data}, upsert=True)
            return await self.user_update(user_id)
        
        return user_info
    
    async def get_user_language(self, user_id):
        user_info = await self.user_update(user_id)
        return user_info.get("language", "uz")

    async def users_list(self):
        return await self.db.users.find().to_list(length=None)
