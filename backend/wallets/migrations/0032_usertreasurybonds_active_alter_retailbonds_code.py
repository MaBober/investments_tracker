# Generated by Django 5.0.3 on 2024-05-02 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0031_remove_retailbonds_issuer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertreasurybonds',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='retailbonds',
            name='code',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
