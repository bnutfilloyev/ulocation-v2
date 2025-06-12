from dataclasses import dataclass, field

from environs import Env

env = Env()
env.read_env()


@dataclass
class BotConfig:
    """Bot configuration."""

    token: str = env.str("TELEGRAM_TOKEN")
    admins: list = field(default_factory=lambda: env.list("ADMIN_IDS"))
    debug: bool = env.bool("DEBUG", False)
    payment_provider_token: str = env.str("CLICK_PAYMENTS_PROVIDER_TOKEN")
    upload_dir: str = env.str("UPLOAD_DIR")


@dataclass
class MongoDBConfig:
    """MongoDB configuration."""

    host: str = env.str("MONGODB_HOST")
    port: int = env.int("MONGODB_PORT")
    username: str = env.str("MONGODB_USERNAME")
    password: str = env.str("MONGODB_PASSWORD")
    database: str = env.str("MONGODB_DATABASE")


@dataclass
class ClickPaymentsConfig:
    merchant_id: str = env.str("CLICK_MERCHANT_ID")
    secret_key: str = env.str("CLICK_SECRET_KEY")
    service_id: str = env.str("CLICK_SERVICE_ID")
    merchant_user_id: str = env.str("CLICK_MERCHANT_USER_ID")

@dataclass
class Configuration:
    """All in one configuration's class."""

    bot = BotConfig()
    db = MongoDBConfig()
    payment = ClickPaymentsConfig()


conf = Configuration()
