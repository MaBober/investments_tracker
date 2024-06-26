# Generated by Django 5.0.3 on 2024-04-18 16:26

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0011_transaction_price_transaction_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userasset',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userasset',
            name='buy_transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='buy_user_assets', to='wallets.transaction'),
        ),
        migrations.AddField(
            model_name='userasset',
            name='commission',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='userasset',
            name='commission_currency',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='user_assets_commission', to='wallets.currency'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userasset',
            name='currency',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='user_assets', to='wallets.currency'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userasset',
            name='currency_price',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=20, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='userasset',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='userasset',
            name='sell_transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sell_user_assets', to='wallets.transaction'),
        ),
    ]
