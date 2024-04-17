from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from . import Currency, Country


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
    dividend_distribution = models.BooleanField(default=False)
    replication_method = models.CharField(max_length=100, blank=False, null=False)

    def save(self, *args, **kwargs):

        self.is_etf = True
        self.full_clean()
        super().save(*args, **kwargs)


class AssetPrice(models.Model):

    asset = models.ForeignKey(MarketAsset, related_name="prices" ,  on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=20, decimal_places=10)
    date = models.DateField()

    class Meta:
        unique_together = ['asset', 'date']

    def __str__(self):
        return f'{self.asset.name} - {self.date}'

    

    

        
