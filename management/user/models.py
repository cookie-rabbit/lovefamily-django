from django.contrib.auth.hashers import make_password, check_password
from django.db import models


# Create your models here.


class User(models.Model):
    """用户表"""
    username = models.CharField(max_length=20, default='')
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    signup_date = models.DateField(null=True)
    status = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    def set_password(self, value):
        self.password = make_password(value)
        self._password = value

    def check_password(self, value):
        return check_password(value, self.password)

    class Meta:
        db_table = 'User'

    def __str__(self):
        return self.username


class UserAddress(models.Model):
    """用户地址"""
    name = models.CharField(max_length=20, null=True)
    province = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=20, null=True)
    district = models.CharField(max_length=20, null=True)
    road = models.CharField(max_length=20, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    postcode = models.CharField(max_length=20, null=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='address')

    class Meta:
        db_table = 'UserAddress'

    def __str__(self):
        return self.name
