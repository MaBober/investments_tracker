# Generated by Django 5.0.3 on 2024-05-15 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0040_remove_retailbonds_current_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='retailbonds',
            name='is_first_year_interest_fixed',
            field=models.BooleanField(default=True),
        ),
    ]
