# Generated by Django 4.1 on 2022-11-28 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_product_customer_start_order_order_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='index',
            field=models.IntegerField(default=None),
        ),
    ]