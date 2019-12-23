from django.db import models
from management import user


# Create your models here.


class Order(models.Model):
    """订单表"""
    order_no = models.CharField(max_length=20)  # 订单编号
    total = models.CharField(max_length=10)  # 总价
    order_date = models.DateField()  # 订单日期
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

    class Meta:
        db_table = "Order"

    def __str__(self):
        return self.user, self.order_no


class OrderAddress(models.Model):
    """订单地址表"""
    name = models.CharField(max_length=40)
    province = models.CharField(max_length=80, default='')
    city = models.CharField(max_length=40, default='')
    district = models.CharField(max_length=40, default='')
    road = models.CharField(max_length=20, default='')
    postcode = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=20)

    class Meta:
        db_table = "OrderAddress"

    def __str__(self):
        return self.name, self.phone_number


class Order_Goods(models.Model):
    """订单--商品表"""
    order = models.ForeignKey("Order", on_delete=models.CASCADE)  # 订单编号
    # goods = models.ForeignKey("goods.Goods", on_delete=models.CASCADE)  # 对应商品
    name_en = models.CharField(max_length=30, null=True)
    img = models.ImageField(default='1.jpg')
    on_price = models.IntegerField(default=0)
    quantity = models.IntegerField()  # 商品数量
    description_en = models.CharField(max_length=500, null=True)

    class Meta:
        db_table = "Order_Goods"
