import datetime

from jinja2 import Template
from mongoengine import (
    CASCADE,
    BooleanField,
    DateTimeField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    ImageField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)
from starlette.requests import Request


class MultilangText(EmbeddedDocument):
    uz = StringField()
    en = StringField()
    ru = StringField()

    async def __admin_repr__(self, request: Request):
        return self.uz or self.en or self.ru or ""


class GeoLocation(EmbeddedDocument):
    """Location coordinates with latitude and longitude."""

    longitude = FloatField()
    latitude = FloatField()

    async def __admin_repr__(self, request: Request):
        if self.latitude is not None and self.longitude is not None:
            return f"({self.latitude}, {self.longitude})"
        return "No coordinates"


class Image(EmbeddedDocument):
    """Image document for storing image data."""

    image = ImageField(required=False)
    caption = StringField()


class Comment(EmbeddedDocument):
    """User comment with rating for a location."""

    user_id = StringField(required=True)
    user_name = StringField()
    text = StringField(required=True)
    rating = FloatField(min_value=1, max_value=5)
    created_at = DateTimeField(default=datetime.datetime.now)

    async def __admin_repr__(self, request: Request):
        return f"Comment by {self.user_id} on {self.created_at}"


class BaseDocument(Document):
    """Base abstract document with common fields."""

    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    meta = {"abstract": True}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)


class City(BaseDocument):
    """City with multilingual name."""

    name = EmbeddedDocumentField(MultilangText, required=True)

    meta = {
        "collection": "cities",
        "ordering": ["name.uz", "name.en"],
        "indexes": ["is_active"],
    }

    async def __admin_repr__(self, request: Request):
        return str(self.name.uz or self.name.en or self.name.ru or "")

    async def __admin_select2_repr__(self, request: Request) -> str:
        template_str = "<span><strong>{{ name }}</strong></span>"
        return Template(template_str, autoescape=True).render(
            name=self.name.uz or self.name.en or self.name.ru or ""
        )


class Category(BaseDocument):
    """Category for locations."""

    name = EmbeddedDocumentField(MultilangText, required=True)

    meta = {
        "collection": "categories",
        "ordering": ["name.uz", "name.en"],
        "indexes": ["is_active"],
    }

    async def __admin_repr__(self, request: Request):
        return str(self.name.uz or self.name.en or self.name.ru or "")

    async def __admin_select2_repr__(self, request: Request) -> str:
        template_str = "<span><strong>{{ name }}</strong></span>"
        return Template(template_str, autoescape=True).render(
            name=self.name.uz or self.name.en or self.name.ru or ""
        )


class Subcategory(BaseDocument):
    """Subcategory for locations."""

    name = EmbeddedDocumentField(MultilangText, required=True)
    category = ReferenceField(Category, reverse_delete_rule=CASCADE, required=True)

    meta = {
        "collection": "subcategories",
        "ordering": ["category", "name.uz", "name.en"],
        "indexes": ["category", "is_active"],
    }

    async def __admin_repr__(self, request: Request):
        return str(self.name.uz or self.name.en or self.name.ru or "")

    def safe_category(self):
        """Safely return the category, handling DoesNotExist errors."""
        try:
            return self.category
        except:
            return None

    async def __admin_select2_repr__(self, request: Request) -> str:
        template_str = "<span><strong>{{ name }}</strong></span>"
        return Template(template_str, autoescape=True).render(
            name=self.name.uz or self.name.en or self.name.ru or ""
        )


class Location(BaseDocument):
    """Location/place with details and geographical coordinates."""

    # Basic information
    name = EmbeddedDocumentField(MultilangText, required=True)
    description = EmbeddedDocumentField(MultilangText)

    # Categorization
    city = ReferenceField(City, required=True, reverse_delete_rule=CASCADE)
    category = ReferenceField(Category, required=True, reverse_delete_rule=CASCADE)
    subcategory = ReferenceField(
        Subcategory, required=True, reverse_delete_rule=CASCADE
    )
    tags = ListField(StringField())

    # Contact and details
    price_range = StringField()  # "$", "$$", "$$$" etc.
    website = StringField()
    phone = StringField()

    # Media
    images = ListField(EmbeddedDocumentField(Image))  # List of images with metadata

    # Geographical data
    location = EmbeddedDocumentField(GeoLocation, required=True)

    # Service integrations
    taxi_link = StringField()
    booking_link = StringField()

    # Rating and feedback
    average_rating = FloatField(min_value=0, max_value=5, default=0)
    rating_count = IntField(default=0, min_value=0)
    comments = ListField(EmbeddedDocumentField(Comment))

    meta = {
        "collection": "locations",
        "ordering": ["-created_at"],
        "indexes": ["city", "category", "subcategory", "tags", "is_active"],
    }

    async def __admin_repr__(self, request: Request):
        return str(self.name)

    def add_comment(self, user_id, text, rating=None):
        """Add a comment and update the average rating."""
        if not user_id or not text:
            return None

        comment = Comment(user_id=user_id, text=text, rating=rating)
        self.comments.append(comment)

        # Update average rating if provided with a valid value
        if rating is not None and 1 <= rating <= 5:
            total_rating = self.average_rating * self.rating_count + rating
            self.rating_count += 1
            self.average_rating = total_rating / self.rating_count

        self.save()
        return comment
