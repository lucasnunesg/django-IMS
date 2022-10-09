# Generated by Django 4.1.1 on 2022-10-09 00:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='last_sales_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='stock_date',
            field=models.DateField(auto_now=True),
        ),
    ]
