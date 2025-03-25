from mongoengine import Document, StringField, DateTimeField, BooleanField, ObjectIdField, IntField, ReferenceField, EmbeddedDocument, EmbeddedDocumentField
import datetime

class PromotionImage(EmbeddedDocument):
    """Embedded document for storing promotion image details"""
    file_id = StringField()
    path = StringField()
    width = IntField()
    height = IntField()

class Promotion(Document):
    """Model for storing promotion campaigns"""
    name = StringField(required=True)
    description = StringField()
    category = StringField()
    partner_id = ObjectIdField()
    image = EmbeddedDocumentField(PromotionImage)
    duration_days = IntField(default=30)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    
    meta = {
        'collection': 'promotions',
        'ordering': ['-created_at'],
        'indexes': [
            'is_active',
            'category',
            'partner_id'
        ]
    }
    
    def __str__(self):
        return self.name

class UserPromoCode(Document):
    """Model for storing user promotion codes"""
    user_id = StringField(required=True)
    promotion_id = ObjectIdField(required=True)
    code = StringField(required=True)
    generated_at = DateTimeField(default=datetime.datetime.now)
    used = BooleanField(default=False)
    
    meta = {
        'collection': 'user_promo_codes',
        'ordering': ['-generated_at'],
        'indexes': [
            'user_id',
            'promotion_id',
            'code',
            'used'
        ]
    }
    
    def __str__(self):
        return f"Promo code {self.code} for user {self.user_id}"
