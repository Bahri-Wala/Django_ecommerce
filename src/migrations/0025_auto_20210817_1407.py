# Generated by Django 3.2.6 on 2021-08-17 13:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0024_userprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='stripe_charge_id',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]