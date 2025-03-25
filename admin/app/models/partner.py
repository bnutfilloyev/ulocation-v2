from mongoengine import Document, StringField, BooleanField, DateTimeField
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
