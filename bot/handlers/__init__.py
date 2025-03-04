from .common import start_router
from handlers.registration import register_router
from handlers.broadcast import broadcast_router
from handlers.subscription import invoices_router
from handlers.promotion import promotions_router
from handlers.partner import partner_router
from handlers.admin import admin_router
from handlers.locations import locations_router

routers = (
    start_router, 
    register_router, 
    broadcast_router, 
    invoices_router, 
    promotions_router,
    partner_router,
    admin_router,
    locations_router,
)
