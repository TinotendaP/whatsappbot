# Generated by Django 4.1 on 2023-02-04 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0009_alter_customer_start_alter_order_order_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='cart_closed',
            field=models.BooleanField(default=False),
        ),
    ]