from mongoengine import Document, StringField, DateTimeField, BooleanField
import datetime

class Referral(Document):
    user_id = StringField(required=True)
    referrer_id = StringField(required=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    paid = BooleanField(default=False)
    
    meta = {
        'collection': 'referrals',
        'ordering': ['-created_at']
    }
    
    def __str__(self):
        return f"{self.user_id} referred by {self.referrer_id}"