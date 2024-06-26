# Generated by Django 5.0.3 on 2024-04-12 09:21

import django.core.validators
import django.db.models.deletion
import wallets.models.abstract
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountInstitutionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='AccountType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssetType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='AccountInstitution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.accountinstitutiontype')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.country')),
            ],
        ),
        migrations.CreateModel(
            name='AssetTypeAssociation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage', models.DecimalField(decimal_places=2, max_digits=3, validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(1)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('asset_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.assettype')),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=100, unique=True)),
                ('symbol', models.CharField(blank=True, max_length=100)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.country')),
            ],
            options={
                'verbose_name_plural': 'Currencies',
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('other_institution', models.CharField(blank=True, max_length=100)),
                ('name', models.CharField(max_length=100, validators=[wallets.models.abstract.validate_name_length])),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_value', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('co_owners', models.ManyToManyField(blank=True, related_name='co_owned_accounts', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to=settings.AUTH_USER_MODEL)),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.accountinstitution')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.accounttype')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.currency')),
            ],
        ),
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('deposited_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deposits', to='wallets.account')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deposits', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeMarket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.country')),
                ('prices_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.currency')),
            ],
        ),
        migrations.CreateModel(
            name='MarketAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('is_tradable', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('asset_type', models.ManyToManyField(related_name='assets', through='wallets.AssetTypeAssociation', to='wallets.assettype')),
                ('exchange_market', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.exchangemarket')),
                ('price_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.currency')),
            ],
            options={
                'unique_together': {('exchange_market', 'code')},
            },
        ),
        migrations.AddField(
            model_name='assettypeassociation',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.marketasset'),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=12)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(default='PLN', max_length=100)),
                ('commission', models.DecimalField(decimal_places=2, max_digits=12)),
                ('commission_currency', models.CharField(default='PLN', max_length=100)),
                ('description', models.TextField(blank=True)),
                ('bought_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='wallets.account')),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, validators=[wallets.models.abstract.validate_name_length])),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('co_owners', models.ManyToManyField(blank=True, related_name='co_owned_wallets', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wallets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('owner', 'name')},
            },
        ),
        migrations.AddField(
            model_name='account',
            name='wallets',
            field=models.ManyToManyField(blank=True, related_name='accounts', to='wallets.wallet'),
        ),
        migrations.CreateModel(
            name='Withdrawal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('withdrawn_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='withdrawals', to='wallets.account')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='withdrawals', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MarketETF',
            fields=[
                ('marketasset_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wallets.marketasset')),
                ('dividend_distribution', models.BooleanField(default=False)),
                ('replication_method', models.CharField(max_length=100)),
                ('fund_country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.country')),
            ],
            bases=('wallets.marketasset',),
        ),
        migrations.CreateModel(
            name='MarketShare',
            fields=[
                ('marketasset_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wallets.marketasset')),
                ('company_country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wallets.country')),
            ],
            bases=('wallets.marketasset',),
        ),
        migrations.AlterUniqueTogether(
            name='assettypeassociation',
            unique_together={('asset', 'asset_type')},
        ),
        migrations.CreateModel(
            name='AssetPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=10, max_digits=20)),
                ('date', models.DateField()),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='prices', to='wallets.marketasset')),
            ],
            options={
                'unique_together': {('asset', 'date')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='account',
            unique_together={('owner', 'name')},
        ),
    ]
