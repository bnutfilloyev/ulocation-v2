from handlers.admin_handlers import admin_routers
from handlers.user_handlers import user_routers
from handlers.partner_handlers import partner_routers

routers = (
    *admin_routers,
    *user_routers,
    *partner_routers,
)
