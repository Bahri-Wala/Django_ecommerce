# Generated by Django 3.2.6 on 2021-08-12 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0018_coupon_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='received',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='refund',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='refund_request',
            field=models.BooleanField(default=False),
        ),
    ]