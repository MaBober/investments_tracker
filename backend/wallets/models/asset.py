import datetime as dt
from dateutil.relativedelta import relativedelta

from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from . import Currency, Country, Account, Wallet, CurrencyPrice

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

    account_currency = models.ForeignKey(Currency, related_name='user_assets', on_delete=models.PROTECT)
    currency_price = models.DecimalField(max_digits=20, decimal_places=10, validators=[MinValueValidator(0)], default=0)

    commission = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)

    buy_transaction = models.ForeignKey('MarketAssetTransaction', related_name='buy_user_assets', on_delete=models.CASCADE, null=True, blank=True)
    sell_transactions = models.ManyToManyField('MarketAssetTransaction', related_name='sell_user_assets', blank=True)

    active = models.BooleanField(default=True, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.asset.name} - {self.amount} {self.currency.code}'

    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def total_price(self):

        price_in_asset_currency = self.amount * self.price

        if self.asset.price_currency != self.account_currency:
            price_in_account_currency = price_in_asset_currency * self.currency_price
        else:
            price_in_account_currency = price_in_asset_currency

        commission = self.commission

        return price_in_account_currency + commission
    
    @property
    def current_value(self):

        try:
            recent_price = self.asset.prices.latest('date').price
        except AssetPrice.DoesNotExist:
            recent_price = self.price

        if self.asset.price_currency != self.account_currency:
            try:
                recent_currency_price = self.asset.price_currency.prices.latest('date').price
            except CurrencyPrice.DoesNotExist:
                recent_currency_price = self.currency_price
            
            return self.amount * recent_price * recent_currency_price
        
        else:

            return self.amount * recent_price
            

class RetailBonds(models.Model):
    
    name = models.CharField(max_length=100, blank=False, null=False)
    code = models.CharField(max_length=100, blank=False, null=False, unique=True)

    description = models.CharField(blank=True, max_length=1000)
    nominal_value = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    duration = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    duration_unit = models.CharField(max_length=1, choices=[('D', 'Days'), ('M', 'Months'), ('Y', 'Years')], blank=False, null=False)

    price_currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT)

    initial_interest_rate = models.DecimalField(max_digits=5, decimal_places=3, validators=[MinValueValidator(Decimal('0.01'))])
    is_intrest_rate_fixed = models.BooleanField(default=True, blank=False, null=False)
    is_first_year_interest_fixed = models.BooleanField(default=True, blank=False, null=False)

    premature_withdrawal_fee = models.DecimalField(max_digits=5, decimal_places=3, validators=[MinValueValidator(Decimal('0.0'))])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def save(self, *args, **kwargs):
    #     if not self.pk and self.current_value is None:
    #         self.current_value = self.nominal_value
    #     elif self.pk and self.current_value is None:  # if the object is being updated and current_value is not set
    #         raise ValueError({"current_value":"current_value cannot be empty during an update"})
    #     super().save(*args, **kwargs)

    @property
    def maturity_date_delta(self):
        if self.duration_unit == 'D':
            return dt.timedelta(days=self.duration)
        if self.duration_unit == 'M':
            return relativedelta(months=self.duration)
        if self.duration_unit == 'Y':
            return relativedelta(years=self.duration)
        

            
        


class TreasuryBonds(RetailBonds):

    def limit_to_bond_countries():
        return {'name__in': [country.name for country in Country.objects.all()]}

    issuer_country = models.ForeignKey(Country, on_delete=models.PROTECT, limit_choices_to=limit_to_bond_countries)

    class Meta:
        verbose_name = 'Treasury Bonds'
        verbose_name_plural = 'Treasury Bonds'

    def save(self, *args, **kwargs):

        if self.issuer_country.name not in [country.name for country in Country.objects.all()]:
            raise ValidationError('Issuer must be a country issuing government bonds.')

        if self.issuer_country == Country.objects.get(name='Poland'):

            self.nominal_value = Decimal('100.00')
            self.price_currency = Currency.objects.get(code='PLN')

        self.asset_type = AssetType.objects.get(name='Treasury Bonds')

        self.clean_fields()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code


class UserTreasuryBonds(models.Model):

    user = models.ForeignKey('auth.User', related_name='bonds', on_delete=models.CASCADE)
    
    account = models.ForeignKey(Account, related_name='bonds', on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, related_name='bonds', on_delete=models.CASCADE)
    bond = models.ForeignKey(RetailBonds, related_name='bonds', on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.0'))])

    issue_date = models.DateField()
    maturity_date = models.DateField()

    buy_transaction = models.ForeignKey('TreasuryBondsTransaction', related_name='buy_user_assets', on_delete=models.CASCADE, null=True, blank=True)
    sell_transactions = models.ManyToManyField('TreasuryBondsTransaction', related_name='sell_user_assets', blank=True)

    active = models.BooleanField(default=True, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Bonds'
        verbose_name_plural = 'User Bonds'

    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def current_value(self):

        years_from_issue = (timezone.now().date() - self.issue_date).days / 365

        if years_from_issue < 1:

            if self.bond.is_intrest_rate_fixed or self.bond.is_first_year_interest_fixed:
                current_single_value = self.__first_year_interest()
            else:
                current_single_value = self.bond.nominal_value
        
        else:
            current_single_value = self.bond.nominal_value

        return current_single_value * self.amount
        
    def __first_year_interest(self):

        days_from_issue = (timezone.now().date() - self.issue_date).days

        if self.__check_if_contains_leap_year():
            daily_interest_rate = self.bond.initial_interest_rate / 366
        else:
            daily_interest_rate = self.bond.initial_interest_rate / 365

        current_interest_rate = round(daily_interest_rate * days_from_issue, 2) / 100
        current_single_value = self.bond.nominal_value  * (1 + current_interest_rate)

        return current_single_value 
        
    def __check_if_contains_leap_year(self):
        import calendar
        ## add a year to the issue date and check if it has a additional day

        year = self.issue_date.year+1
        _, days_in_feb = calendar.monthrange(year, 2)

        return days_in_feb == 29
 





