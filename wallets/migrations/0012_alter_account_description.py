# Generated by Django 5.0.3 on 2024-04-08 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0011_alter_account_current_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='description',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
