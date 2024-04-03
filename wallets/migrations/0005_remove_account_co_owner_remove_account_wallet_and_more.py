# Generated by Django 5.0.3 on 2024-04-03 16:38

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0004_alter_account_co_owner_alter_wallet_co_owner'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='co_owner',
        ),
        migrations.RemoveField(
            model_name='account',
            name='wallet',
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='co_owner',
        ),
        migrations.AddField(
            model_name='account',
            name='co_owner',
            field=models.ManyToManyField(blank=True, related_name='co_owned_accounts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='account',
            name='wallet',
            field=models.ManyToManyField(related_name='accounts', to='wallets.wallet'),
        ),
        migrations.AddField(
            model_name='wallet',
            name='co_owner',
            field=models.ManyToManyField(blank=True, related_name='co_owned_wallets', to=settings.AUTH_USER_MODEL),
        ),
    ]
