from .base import MongoDB


class PartnerDB(MongoDB):
    async def get_partner(self, login: str):
        return await self.db.partners.find_one({"login": login})

    async def get_parners(self):
        return await self.db.partners.find().to_list(length=None)

    async def check_partner_credentials(self, login: str, password: str):
        partner = await self.get_partner(login)
        if partner and partner.get("password") == password:
            return partner
        return None