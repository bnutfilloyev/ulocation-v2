from .base import MongoDB
from .locations import LocationDB
from .partners import PartnerDB
from .promotions import PromotionDB
from .referrals import ReferralDB
from .users import UserDB

# Create instances for direct import
db = MongoDB()
user_db = UserDB()
partner_db = PartnerDB()
promotion_db = PromotionDB()
referral_db = ReferralDB()
location_db = LocationDB()
