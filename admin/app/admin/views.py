from starlette_admin.contrib.mongoengine import Admin
from app.utils.auth import MyAuthProvider

admin = Admin(
    title="ULocation Admin",
    base_url="/admin",
    route_name="admin",
    auth_provider=MyAuthProvider(login_path="/sign-in", logout_path="/sign-out"),
)

# Register models with admin
from starlette_admin.contrib.mongoengine import ModelView
from app.models.partner import Partner
from app.models.promotion import Promotion, UserPromoCode
from app.models.referral import Referral
from app.models.user import User
from app.models.location import City, Category, Subcategory, Location

def register_admin_views(admin):
    """Register all model views with the admin instance"""
    admin.add_view(ModelView(Partner, name="Partners", icon="fa fa-user-tie"))
    admin.add_view(ModelView(Promotion, name="Promotions", icon="fa fa-gift"))
    admin.add_view(ModelView(UserPromoCode, name="User Promo Codes", icon="fa fa-ticket-alt"))
    admin.add_view(ModelView(Referral, name="Referrals", icon="fa fa-users"))
    admin.add_view(ModelView(User, name="Users", icon="fa fa-user"))
    admin.add_view(ModelView(City, name="Cities", icon="fa fa-city"))
    admin.add_view(ModelView(Category, name="Categories", icon="fa fa-tag"))
    admin.add_view(ModelView(Subcategory, name="Subcategories", icon="fa fa-tags"))
    admin.add_view(ModelView(Location, name="Locations", icon="fa fa-map-marker-alt"))

register_admin_views(admin)