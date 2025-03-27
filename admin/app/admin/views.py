from typing import Any, Dict

from app.utils.auth import MyAuthProvider
from starlette.datastructures import FormData
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.contrib.mongoengine import Admin
from starlette_admin.exceptions import FormValidationError

admin = Admin(
    title="ULocation Admin",
    base_url="/admin",
    route_name="admin",
    auth_provider=MyAuthProvider(login_path="/sign-in", logout_path="/sign-out"),
)

from app.models.location import Category, City, Location, Subcategory
from app.models.partner import Partner, Promotion, UserPromoCode
from app.models.referral import Referral
from app.models.user import User
from markupsafe import Markup
from starlette_admin import RequestAction, TagsField, TextAreaField
from starlette_admin.contrib.mongoengine import ModelView


class HTMLField(TextAreaField):
    async def serialize_value(self, request, value, action: RequestAction):
        if action == RequestAction.DETAIL:
            if value:
                html_value = value.replace("\n", "<br>")
                return Markup(html_value)
            return "-"
        return await super().serialize_value(request, value, action)


class PromotionView(ModelView):
    fields = [
        "name",
        HTMLField("description"),
        "category",
        "partner_id",
        "image",
        "is_active",
        "created_at",
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        if data["partner_id"] is None:
            raise FormValidationError("Partner is required")
        return await super().validate(request, data)

    exclude_fields_from_list = ["description"]
    exclude_fields_from_create = ["created_at"]
    exclude_fields_from_edit = ["created_at"]

    sortable_fields = ["name", "category", "partner_id", "is_active", "created_at"]
    search_fields = ["_id", "name", "category", "partner_id", "is_active", "created_at"]


class LocationView(ModelView):
    fields = [
        "name",
        "description",
        "city",
        "category",
        "subcategory",
        TagsField("tags"),
        "price_range",
        "website",
        "phone",
        "images",
        "location",
        "taxi_link",
        "booking_link",
        "average_rating",
        "rating_count",
        "comments",
        "is_active",
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_list = [
        "price_range",
        "website",
        "phone",
        "taxi_link",
        "booking_link",
        "average_rating",
        "rating_count",
        "location",
        "description",
        "comments",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_create = ["created_at", "updated_at"]
    exclude_fields_from_edit = ["created_at", "updated_at"]

    sortable_fields = [
        "name",
        "city_id",
        "category_id",
        "subcategory_id",
        "is_active",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "_id",
        "name",
        "city_id",
        "category_id",
        "subcategory_id",
        "is_active",
        "created_at",
        "updated_at",
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        if data["city"] is None:
            raise FormValidationError("City is required")
        if data["category"] is None:
            raise FormValidationError("Category is required")
        if data["subcategory"] is None:
            raise FormValidationError("Subcategory is required")
        return await super().validate(request, data)


def register_admin_views(admin):
    """Register all model views with the admin instance"""
    admin.add_view(
        ModelView(Partner, name="Partners", icon="fa fa-user-tie", label="Partners")
    )
    admin.add_view(
        PromotionView(
            Promotion, name="Promotions", icon="fa fa-gift", label="Promotions"
        )
    )
    admin.add_view(
        ModelView(
            UserPromoCode,
            name="User Promo Codes",
            icon="fa fa-ticket-alt",
            label="User Promo Codes",
        )
    )
    admin.add_view(
        ModelView(Referral, name="Referrals", icon="fa fa-users", label="Referrals")
    )
    admin.add_view(ModelView(User, name="Users", icon="fa fa-user", label="Users"))
    admin.add_view(ModelView(City, name="Cities", icon="fa fa-city", label="Cities"))
    admin.add_view(
        ModelView(Category, name="Categories", icon="fa fa-tag", label="Categories")
    )
    admin.add_view(
        ModelView(
            Subcategory, name="Subcategories", icon="fa fa-tags", label="Subcategories"
        )
    )
    admin.add_view(
        LocationView(
            Location, name="Locations", icon="fa fa-map-marker-alt", label="Locations"
        )
    )


register_admin_views(admin)
