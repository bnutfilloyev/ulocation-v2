from handlers.user_handlers.common import start_router
from handlers.user_handlers.locations import locations_router
from handlers.user_handlers.promotion import promotions_router
from handlers.user_handlers.referral import referral_router
from handlers.user_handlers.registration import register_router
from handlers.user_handlers.subscription import invoices_router

user_routers = (
    start_router,
    register_router,
    invoices_router,
    promotions_router,
    locations_router,
    referral_router,
)
