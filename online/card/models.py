from django.db import models
from management import user
from management.user.models import User

# Create your models here.

class Card(models.Model):
    """信用卡"""
    cardid = models.CharField(max_length=20)
    name = models.CharField(max_length=10)
    user = models.ForeignKey("user.User",on_delete=models.CASCADE,related_name="cards")

    class Meta:
        db_table = "Card"

    def __str__(self):
        return self.cardid