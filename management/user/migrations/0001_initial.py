# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-01-14 10:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='admin', max_length=40)),
                ('password', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'Admin',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='', max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=40)),
                ('password', models.CharField(max_length=100)),
                ('signup_date', models.DateField(null=True)),
                ('status', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'User',
            },
        ),
        migrations.CreateModel(
            name='UserAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, null=True)),
                ('province', models.CharField(max_length=100, null=True)),
                ('city', models.CharField(max_length=100, null=True)),
                ('district', models.CharField(max_length=100, null=True)),
                ('road', models.CharField(max_length=100, null=True)),
                ('phone_number', models.CharField(max_length=40, null=True)),
                ('postcode', models.CharField(max_length=40, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='address', to='user.User')),
            ],
            options={
                'db_table': 'UserAddress',
            },
        ),
    ]
