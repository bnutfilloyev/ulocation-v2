from urllib.parse import quote_plus

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
