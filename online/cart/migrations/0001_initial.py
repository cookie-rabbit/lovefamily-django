# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-01-14 10:48
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
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('goods', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='goods.Goods')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='user.User')),
            ],
            options={
                'db_table': 'Cart',
            },
        ),
    ]
