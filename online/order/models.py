from django.db import models
from management import user
# Create your models here.


class Order(models.Model):
    """订单表"""
    order_no = models.CharField(max_length=20)
    total = models.CharField(max_length=10)
    order_date = models.DateField()
    choices = (
        (0,"Payed"),
        (1,"Delivering"),
        (2,"Finished")
    )
    status = models.IntegerField(choices=choices)
    address = models.ForeignKey("OrderAddress",on_delete=models.CASCADE,related_name='order')
    user = models.ForeignKey('user.User',on_delete=models.CASCADE,related_name='order')

    class Meta:
        db_table = "Order"

    def __str__(self):
        return (self.user,self.order_no)


class OrderAddress(models.Model):
    """订单地址表"""
    name = models.CharField(max_length=20)
    province = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    district = models.CharField(max_length=20,default='')
    road = models.CharField(max_length=20,default='')
    postcode = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)

    class Meta:
        db_table = "OrderAddress"

    def __str__(self):
        return (self.name,self.mobile)


class Order_Goods(models.Model):
    """订单--商品表"""
    order = models.ForeignKey("Order",on_delete=models.CASCADE)
    goods = models.ForeignKey("goods.Goods",on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        db_table = "Order_Goods"
