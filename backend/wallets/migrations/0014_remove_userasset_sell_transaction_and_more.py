# Generated by Django 5.0.3 on 2024-04-18 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0013_remove_transaction_user_asset'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userasset',
            name='sell_transaction',
        ),
        migrations.AddField(
            model_name='userasset',
            name='sell_transaction',
            field=models.ManyToManyField(blank=True, null=True, related_name='sell_user_assets', to='wallets.transaction'),
        ),
    ]