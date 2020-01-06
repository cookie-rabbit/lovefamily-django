# Generated by Django 2.2.1 on 2019-12-26 10:06

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
                ('origin_price', models.IntegerField(default=0)),
                ('on_price', models.IntegerField(default=0)),
                ('actual_sale', models.IntegerField(default=0)),
                ('virtual_sale', models.IntegerField(default=0)),
                ('on_sale', models.BooleanField()),
                ('description_ch', models.CharField(max_length=500, null=True)),
                ('description_en', models.CharField(max_length=500, null=True)),
                ('detail_ch', models.TextField(null=True)),
                ('detail_en', models.TextField(null=True)),
                ('stock', models.IntegerField()),
                ('is_hot', models.BooleanField(default=False)),
                ('is_new', models.BooleanField(default=False)),
                ('added_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goods', to='goods.Category')),
            ],
            options={
                'db_table': 'Goods',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='1.jpg', upload_to='')),
                ('goods', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='goods.Goods')),
            ],
        ),
    ]