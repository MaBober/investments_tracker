# Generated by Django 5.0.3 on 2024-04-25 19:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0020_remove_account_currency_account_currencies'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='commission_currency_price',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=20, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
