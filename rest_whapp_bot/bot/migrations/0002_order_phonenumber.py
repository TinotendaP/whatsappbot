# Generated by Django 4.1 on 2022-11-25 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='phonenumber',
            field=models.BigIntegerField(default=0),
        ),
    ]
