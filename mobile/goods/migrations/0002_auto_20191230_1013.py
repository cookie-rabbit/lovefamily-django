# Generated by Django 2.2.1 on 2019-12-30 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='on_price',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
