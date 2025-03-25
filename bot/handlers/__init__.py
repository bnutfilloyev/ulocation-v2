from handlers.admin_handlers import admin_routers
from handlers.influencer_handlers import influencer_routers
from handlers.partner_handlers import partner_routers
from handlers.user_handlers import user_routers

routers = (
    *admin_routers,
    *user_routers,
    *partner_routers,
)
