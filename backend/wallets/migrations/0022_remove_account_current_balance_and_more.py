# Generated by Django 5.0.3 on 2024-04-30 11:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0021_transaction_commission_currency_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='current_balance',
        ),
        migrations.CreateModel(
            name='AccountCurrencyBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='balances', to='wallets.account')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallets.currency')),
            ],
            options={
                'unique_together': {('account', 'currency')},
            },
        ),
    ]