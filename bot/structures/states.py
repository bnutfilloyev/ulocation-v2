from aiogram.filters.state import State, StatesGroup


class RegState(StatesGroup):
    fullname = State()
    phone_number = State()
    agreement = State()
    subscription = State()

class PaymentState(StatesGroup):
    waiting_for_card_number = State()
    waiting_for_card_expiration = State()
    waiting_for_sms_code = State()


class BroadcastState(StatesGroup):
    broadcast = State()


class PartnerAddState(StatesGroup):
    waiting_for_partner_name = State()
    waiting_for_partner_login = State()
    waiting_for_partner_password = State()


class PartnerAuthState(StatesGroup):
    waiting_for_partner_login = State()
    waiting_for_partner_password = State()
    waiting_for_promo_code = State()


class AddPromotionState(StatesGroup):
    waiting_for_promotion_name = State()
    waiting_for_promotion_description = State()
    waiting_for_promotion_image = State()
    waiting_for_promotion_category = State()


class AddCommentState(StatesGroup):
    waiting_for_rating = State()
    waiting_for_comment_text = State()


class SponsorshipForm(StatesGroup):
    social_links = State()
    additional_info = State()