# Generated by Django 5.0.3 on 2024-04-17 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0006_assetprice_created_at_assetprice_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetprice',
            name='source',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
