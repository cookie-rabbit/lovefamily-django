# Generated by Django 2.2.1 on 2019-12-30 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0004_category_is_show'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='is_show',
        ),
        migrations.AddField(
            model_name='category',
            name='disabled',
            field=models.IntegerField(default=0),
        ),
    ]