from mongoengine import Document, StringField, DateTimeField, BooleanField, ReferenceField, ImageField, CASCADE, NULLIFY
from app.models.user import User

import datetime



class Partner(Document):
    name = StringField(max_length=255, required=True)
    login = StringField(max_length=100, required=True, unique=True)
    password = StringField(max_length=255, required=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    is_active = BooleanField(default=True)
    
    meta = {
        'collection': 'partners',
        'indexes': ['login'],
        'ordering': ['-created_at']
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    
    def __str__(self):
        return self.name



class Promotion(Document):
    """Model for storing promotion campaigns"""
    name = StringField(required=True)
    description = StringField(required=True)
    category = StringField(required=True) 
    partner_id = ReferenceField(Partner, reverse_delete_rule=CASCADE, required=True)
    image = ImageField(size=(800, 800), thumbnail_size=(200, 200), collection_name='promotion_images')
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
    promotion_id = ReferenceField(Promotion, reverse_delete_rule=NULLIFY, required=True)
    code = StringField(required=True)
    generated_at = DateTimeField(default=datetime.datetime.now)
    used = BooleanField(default=False)
    used_at = DateTimeField()
    
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

