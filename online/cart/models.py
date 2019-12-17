from django.db import models
from management import user
# Create your models here.


class Cart(models.Model):
    """购物车"""
    user = models.ForeignKey('user.User',on_delete=models.CASCADE,related_name='cart')
    goods = models.ForeignKey("goods.Goods", on_delete=models.CASCADE,default='')
    quantity = models.IntegerField(default=0)

    class Meta:
        db_table = "Cart"

    def __str__(self):
        return self.user.phone

