# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-12-19 07:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0002_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goods',
            name='price',
        ),
        migrations.AddField(
            model_name='goods',
            name='on_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='goods',
            name='origin_price',
            field=models.IntegerField(default=0),
        ),
    ]
