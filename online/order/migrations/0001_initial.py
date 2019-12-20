# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-12-19 06:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.CharField(max_length=20)),
                ('total', models.CharField(max_length=10)),
                ('order_date', models.DateField()),
                ('status', models.IntegerField(choices=[(0, 'Payed'), (1, 'Delivering'), (2, 'Finished')])),
            ],
            options={
                'db_table': 'Order',
            },
        ),
        migrations.CreateModel(
            name='Order_Goods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('goods', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='goods.Goods')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.Order')),
            ],
            options={
                'db_table': 'Order_Goods',
            },
        ),
        migrations.CreateModel(
            name='OrderAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('province', models.CharField(max_length=20)),
                ('city', models.CharField(max_length=20)),
                ('district', models.CharField(default='', max_length=20)),
                ('road', models.CharField(default='', max_length=20)),
                ('postcode', models.CharField(max_length=10)),
                ('phone', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'OrderAddress',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='order.OrderAddress'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='user.User'),
        ),
    ]