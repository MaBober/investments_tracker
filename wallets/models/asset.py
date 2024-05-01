from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from . import Currency, Country, Account, Wallet

def past_or_present_date(value):
    if value > timezone.now().date():
        raise ValidationError('Date cannot be in the future.')

class AssetType(models.Model):

    name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    description = models.CharField(blank=True, max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)       
        

class ExchangeMarket(models.Model):

    name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    code = models.CharField(max_length=100, blank=False, null=False, unique=True)
    description = models.CharField(blank=True, max_length=1000)
    prices_currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)  


class MarketAsset(models.Model):
    
    name = models.CharField(max_length=100, blank=False, null=False)
    code = models.CharField(max_length=100, blank=False, null=False)
    is_etf = models.BooleanField(default=False, editable=False)
    is_share = models.BooleanField(default=False, editable=False)
    description = models.CharField(blank=True, max_length=1000)
    exchange_market = models.ForeignKey(ExchangeMarket, on_delete=models.PROTECT)
    price_currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    asset_type = models.ManyToManyField(AssetType, related_name='assets', through='AssetTypeAssociation')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = ['exchange_market', 'code']

    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)  


class AssetTypeAssociation(models.Model):
    
    asset = models.ForeignKey(MarketAsset, on_delete=models.CASCADE)
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT)

    percentage = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0.01), MaxValueValidator(1)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['asset', 'asset_type']

    def clean(self) -> None:
        super().clean()

        if self.asset.is_share:
            if self.asset_type.name == 'Share' and self.percentage != 1:
                raise ValidationError('Share must have percentage 1')
        
            if self.asset_type.name != 'Share' :
                raise ValidationError('MarketShare must have AssetType Share with percentage 1')
        
        if self.asset.is_etf:

            total_percentage = Decimal(self.percentage)
            for type_used in self.asset.assettypeassociation_set.all():
                total_percentage += type_used.percentage

            total_percentage = total_percentage.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP) 
            if total_percentage > 1:
                raise ValidationError(f'Total percentage must be 1. Current total is {total_percentage}')

    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)
                
   
class MarketShare(MarketAsset):

    company_country = models.ForeignKey(Country, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        is_new = self.id is None

        self.is_share = True
        self.full_clean()
        super().save(*args, **kwargs)

        if is_new:
            AssetTypeAssociation.objects.create(asset=self, asset_type=AssetType.objects.get(name='Share'), percentage=1)


class MarketETF(MarketAsset):

    fund_country = models.ForeignKey(Country, on_delete=models.PROTECT)
    dividend_distribution = models.BooleanField(default=False, blank=False, null=False)
    replication_method = models.CharField(max_length=100, blank=False, null=False)

    def save(self, *args, **kwargs):

        self.is_etf = True
        self.full_clean()
        super().save(*args, **kwargs)


class AssetPrice(models.Model):

    asset = models.ForeignKey(MarketAsset, related_name="prices",  on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=20, decimal_places=10, validators=[MinValueValidator(0)])
    date = models.DateField(validators=[past_or_present_date], null=False, blank=False)
    source = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['asset', 'date']

    def __str__(self):
        return f'{self.asset.name} - {self.date} - {self.price} {self.asset.price_currency.code}'

    def save(self, *args, **kwargs):

        if self.id is not None:  # If the instance has already been saved to the database
            raise ValidationError('Updating a asset price is not allowed.')
        
        self.full_clean()
        super().save(*args, **kwargs)


class UserAsset(models.Model):

    user = models.ForeignKey('auth.User', related_name='assets', on_delete=models.CASCADE)
    
    account = models.ForeignKey(Account, related_name='assets', on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, related_name='assets', on_delete=models.CASCADE)

    asset = models.ForeignKey(MarketAsset, related_name='users', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)

    currency = models.ForeignKey(Currency, related_name='user_assets', on_delete=models.PROTECT)
    currency_price = models.DecimalField(max_digits=20, decimal_places=10, validators=[MinValueValidator(0)], default=0)

    commission = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    commission_currency = models.ForeignKey(Currency, related_name='user_assets_commission', on_delete=models.PROTECT)    

    buy_transaction = models.ForeignKey('MarketAssetTransaction', related_name='buy_user_assets', on_delete=models.CASCADE, null=True, blank=True)
    sell_transaction = models.ManyToManyField('MarketAssetTransaction', related_name='sell_user_assets', blank=True)

    active = models.BooleanField(default=True, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.asset.name} - {self.amount} {self.currency.code}'

    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)
            

class RetailBonds(models.Model):
    
    name = models.CharField(max_length=100, blank=False, null=False)
    code = models.CharField(max_length=100, blank=False, null=False)

    description = models.CharField(blank=True, max_length=1000)
    issuer = models.CharField(max_length=100, blank=False, null=False)
    nominal_value = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    price_currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT)
    current_value = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    initial_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    premature_withdrawal_fee = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TreasuryBonds(RetailBonds):

    def limit_to_bond_countries():
        return {'name__in': [country.name for country in Country.objects.all()]}

    issuer_country = models.ForeignKey(Country, on_delete=models.PROTECT, limit_choices_to=limit_to_bond_countries)

    class Meta:
        verbose_name = 'Government Bonds'
        verbose_name_plural = 'Government Bonds'

    def save(self, *args, **kwargs):

        if self.issuer.name not in [country.name for country in Country.objects.all()]:
            raise ValidationError('Issuer must be a country issuing government bonds.')

        if self.issuer_country == Country.objects.get(name='Poland'):

            self.nominal_value = Decimal('100.00')
            self.price_currency = Currency.objects.get(code='PLN')
            self.asset_type = AssetType.objects.get(name='Government Bonds')

        self.asset_type = AssetType.objects.get(name='Government Bonds')

        self.full_clean()
        super().save(*args, **kwargs)


class UserTreasuryBonds(models.Model):

    user = models.ForeignKey('auth.User', related_name='bonds', on_delete=models.CASCADE)
    
    account = models.ForeignKey(Account, related_name='bonds', on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, related_name='bonds', on_delete=models.CASCADE)
    bond = models.ForeignKey(RetailBonds, related_name='bonds', on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    issue_date = models.DateField()
    maturity_date = models.DateField()

    buy_transaction = models.ForeignKey('TreasuryBondsTransaction', related_name='buy_user_assets', on_delete=models.CASCADE, null=True, blank=True)
    sell_transaction = models.ManyToManyField('TreasuryBondsTransaction', related_name='sell_user_assets', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Bonds'
        verbose_name_plural = 'User Bonds'

    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)

