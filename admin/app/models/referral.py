import datetime

from mongoengine import BooleanField, DateTimeField, Document, StringField


class Referral(Document):
    user_id = StringField(required=True)
    referrer_id = StringField(required=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    paid = BooleanField(default=False)
    payment_date = DateTimeField()
    referral_user_id = StringField()
    payment_status = StringField(default="pending")

    meta = {"collection": "referral_payments", "ordering": ["-created_at"]}

    def __str__(self):
        return f"{self.user_id} referred by {self.referrer_id}"
