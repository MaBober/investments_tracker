# Generated by Django 5.0.3 on 2024-04-18 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0014_remove_userasset_sell_transaction_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userasset',
            name='sell_transaction',
            field=models.ManyToManyField(blank=True, related_name='sell_user_assets', to='wallets.transaction'),
        ),
    ]