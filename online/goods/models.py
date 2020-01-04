from django.db import models
from django.utils import timezone
# Create your models here.
from datetime import datetime


class Goods(models.Model):
    """商品表"""
    name_ch = models.CharField(max_length=20, null=True)
    name_en = models.CharField(max_length=30, null=True)
    origin_price = models.FloatField(default=None, null=True)
    on_price = models.FloatField(default=0)
    actual_sale = models.IntegerField(default=0)
    virtual_sale = models.IntegerField(default=0)
    on_sale = models.BooleanField()
    description_ch = models.CharField(max_length=500, null=True)
    description_en = models.CharField(max_length=500, null=True)
    detail_ch = models.TextField(null=True)
    detail_en = models.TextField(null=True)
    stock = models.IntegerField()
    is_hot = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    added_time = models.DateTimeField()
    super_category_id = models.CharField(max_length=10, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='goods')

    class Meta:
        db_table = "Goods"

    def __str__(self):
        return self.name_en


class Image(models.Model):
    """商品图片"""
    image = models.ImageField(default='1.jpg')
    goods = models.ForeignKey('Goods', on_delete=models.CASCADE, related_name='images')

    class Meat:
        db_table = "Image"

    def __str__(self):
        return self.image.url


class Category(models.Model):
    """商品种类表"""
    name = models.CharField(max_length=30)
    super_category = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    disabled = models.IntegerField(default=0)

    class Meta:
        db_table = "Category"

    def __str__(self):
        return self.name
