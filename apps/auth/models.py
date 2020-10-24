from tortoise.models import Model
from tortoise import fields


class User(Model):
    """User model in database"""
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255)
    wins = fields.IntField(default=0)

    def __str__(self):
        return self.username