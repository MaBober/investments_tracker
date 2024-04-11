# Generated by Django 5.0.3 on 2024-04-08 20:59

import wallets.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0009_rename_co_owner_wallet_co_owners'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='co_owner',
            new_name='co_owners',
        ),
        migrations.AlterField(
            model_name='account',
            name='description',
            field=models.TextField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='account',
            name='name',
            field=models.CharField(max_length=100, validators=[wallets.models.validate_name_length]),
        ),
        migrations.AlterUniqueTogether(
            name='account',
            unique_together={('owner', 'name')},
        ),
    ]
