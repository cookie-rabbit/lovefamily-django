import pytz
from django.db import models
from management import user


# Create your models here.


class Order(models.Model):
    """订单表"""
    order_no = models.CharField(max_length=40)  # 订单编号
    total = models.CharField(max_length=10)  # 总价
    order_date = models.DateTimeField()  # 订单日期
    choices = (  # 订单状态列表
        (0, "ALL"),
        (1, "Ordered"),
        (2, "Payed"),
        (3, "Delivering"),
        (4, "Finished"),
        (5, "Closed"),
    )
    status = models.IntegerField(choices=choices, default=0)  # 订单状态
    address = models.ForeignKey("OrderAddress", on_delete=models.CASCADE, related_name='order')  # 订单地址
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='order')  # 订单用户
    paid_date = models.DateTimeField(null=True)

    class Meta:
        db_table = "Order"

    def __str__(self):
        return self.user, self.order_no


class OrderAddress(models.Model):
    """订单地址表"""
    name = models.CharField(max_length=40, null=True)
    province = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    district = models.CharField(max_length=100, null=True)
    road = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=40, null=True)
    postcode = models.CharField(max_length=40, null=True)

    class Meta:
        db_table = "OrderAddress"

    def __str__(self):
        return self.name, self.phone_number


class Order_Goods(models.Model):
    """订单--商品表"""
    order = models.ForeignKey("Order", on_delete=models.CASCADE)  # 订单编号
    goods = models.ForeignKey("goods.Goods", on_delete=models.CASCADE, null=True)  # 对应商品
    name_en = models.CharField(max_length=30, null=True)
    img = models.ImageField(default='1.jpg')
    on_price = models.IntegerField(default=0)
    quantity = models.IntegerField()  # 商品数量
    description_en = models.CharField(max_length=500, null=True)

    class Meta:
        db_table = "Order_Goods"


class OrderStatusLog(models.Model):
    """订单状态修改历史表"""
    order_no = models.CharField(max_length=40)
    status = models.IntegerField()
    user_id = models.CharField(max_length=40)
    change_date = models.DateTimeField()
    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = "OrderStatusLog"

