# Generated by Django 5.0.3 on 2024-04-09 13:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0017_country_alter_accountinstitution_country_currency_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='country',
            old_name='short_name',
            new_name='code',
        ),
        migrations.RenameField(
            model_name='currency',
            old_name='short_name',
            new_name='code',
        ),
    ]
