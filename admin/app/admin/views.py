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
from starlette_admin.fields import TextAreaField

from app.models.partner import Partner, Promotion, UserPromoCode
from app.models.referral import Referral
from app.models.user import User
from app.models.location import City, Category, Subcategory, Location

class PromotionAdmin(ModelView):
    fields = [
        "name",
        TextAreaField("description"),
        "category",
        "image",
        "is_active",
        "created_at"
    ]


def register_admin_views(admin):
    """Register all model views with the admin instance"""
    admin.add_view(ModelView(Partner, name="Partners", icon="fa fa-user-tie", label="Partners"))
    admin.add_view(PromotionAdmin(Promotion, name="Promotions", icon="fa fa-gift", label="Promotions"))
    admin.add_view(ModelView(UserPromoCode, name="User Promo Codes", icon="fa fa-ticket-alt", label="User Promo Codes"))
    admin.add_view(ModelView(Referral, name="Referrals", icon="fa fa-users", label="Referrals"))
    admin.add_view(ModelView(User, name="Users", icon="fa fa-user", label="Users"))
    admin.add_view(ModelView(City, name="Cities", icon="fa fa-city", label="Cities"))
    admin.add_view(ModelView(Category, name="Categories", icon="fa fa-tag", label="Categories"))
    admin.add_view(ModelView(Subcategory, name="Subcategories", icon="fa fa-tags", label="Subcategories"))
    admin.add_view(ModelView(Location, name="Locations", icon="fa fa-map-marker-alt", label="Locations"))

register_admin_views(admin)