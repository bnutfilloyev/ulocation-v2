import random
import string
from datetime import datetime
from urllib.parse import quote_plus

from bson.objectid import ObjectId
from motor import motor_asyncio

from configuration import conf


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


db = MongoDB()


class LocationDB(MongoDB):
    async def get_cities(self):
        return await self.db.myapp_city.find().to_list(length=None)
    
location_db = LocationDB()