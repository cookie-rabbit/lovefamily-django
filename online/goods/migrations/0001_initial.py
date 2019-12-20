# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-12-19 06:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('super_category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='goods.Category')),
            ],
            options={
                'db_table': 'Category',
            },
        ),
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ch', models.CharField(max_length=20, null=True)),
                ('name_en', models.CharField(max_length=30, null=True)),
                ('price', models.IntegerField()),
                ('sale', models.IntegerField()),
                ('on_sale', models.BooleanField()),
                ('description_ch', models.CharField(max_length=500, null=True)),
                ('description_en', models.CharField(max_length=500, null=True)),
                ('detail_ch', models.CharField(max_length=500, null=True)),
                ('detail_en', models.CharField(max_length=500, null=True)),
                ('stock', models.IntegerField()),
                ('is_hot', models.BooleanField(default=False)),
                ('added_time', models.DateField(default=django.utils.timezone.now)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goods', to='goods.Category')),
            ],
            options={
                'db_table': 'Goods',
            },
        ),
    ]