import datetime

from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    ListField,
    StringField,
)


class Payment(EmbeddedDocument):
    payment_id = StringField(required=True)
    payment_date = DateTimeField()
    amount = FloatField()
    currency = StringField(default="UZS")

    meta = {"indexes": ["payment_id"]}


class User(Document):
    user_id = StringField(required=True, unique=True)
    username = StringField(sparse=True)
    first_name = StringField()
    last_name = StringField()
    input_fullname = StringField()
    input_phone = StringField()
    language = StringField(default="uz")
    agreement = BooleanField(default=False)

    is_subscribed = BooleanField(default=False)
    expiry_date = DateTimeField()
    payments = ListField(EmbeddedDocumentField(Payment))
    referral_bonus_months = FloatField(default=0)
    referral_count = FloatField(default=0)
    referrer_id = StringField()

    # System fields
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)
    is_sponsor = BooleanField(default=False)

    meta = {
        "collection": "users",
        "ordering": ["-created_at"],
        "indexes": ["user_id", "username", "is_subscribed", "expiry_date", "is_admin"],
        "dynamic": True,
    }

    def __str__(self):
        return (
            self.input_fullname
            or f"{self.first_name} {self.last_name}".strip()
            or f"User {self.user_id}"
        )

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(User, self).save(*args, **kwargs)

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.input_fullname:
            return self.input_fullname
        return self.username or f"User {self.user_id}"

    @property
    def is_subscription_active(self):
        if not self.is_subscribed or not self.expiry_date:
            return False
        return self.expiry_date > datetime.datetime.now()
