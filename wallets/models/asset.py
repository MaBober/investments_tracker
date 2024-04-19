from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.db.models import Sum
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

    buy_transaction = models.ForeignKey('Transaction', related_name='buy_user_assets', on_delete=models.CASCADE, null=True, blank=True)
    sell_transaction = models.ManyToManyField('Transaction', related_name='sell_user_assets', blank=True)

    active = models.BooleanField(default=True, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.asset.name} - {self.amount} {self.currency.code}'

    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)

    
    @staticmethod
    def sell_assets(transaction):

        user_assets = transaction.user.assets.objects.filter(asset=transaction.asset, active=True).order_by('created_at')

        for user_asset in user_assets:
            print("amount", transaction.amount)
            if user_asset.amount > transaction.amount:
                user_asset.amount -= transaction.amount
                user_asset.sell_transaction.add(transaction)
                user_asset.save()

                break
            
            elif user_asset.amount == transaction.amount:
                user_asset.active = False
                user_asset.amount = 0
                user_asset.sell_transaction.add(transaction)
                user_asset.save()
                break

            else:
                transaction.amount -= user_asset.amount
                user_asset.active = False
                user_asset.amount = 0
                user_asset.sell_transaction.add(transaction)
                user_asset.save()

    @staticmethod
    def buy_assets(transaction):

        user_asset = UserAsset.objects.create(
            user=transaction.user,
            account=transaction.account,
            wallet=transaction.wallet,
            asset=transaction.asset,
            amount=transaction.amount,
            price=transaction.price,
            currency=transaction.currency,
            currency_price=transaction.currency_price,
            commission=transaction.commission,
            commission_currency=transaction.commission_currency,
            buy_transaction=transaction,
            active=True
        )
        user_asset.save()
            

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('S', 'Sell'),
        ('B', 'Buy'),
    ]

    user = models.ForeignKey('auth.User', related_name='transactions', on_delete=models.CASCADE)

    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPES, blank=False, null=False)

    account = models.ForeignKey(Account, related_name='transactions', on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, related_name='transactions', on_delete=models.CASCADE)

    asset = models.ForeignKey(MarketAsset, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)

    currency = models.ForeignKey(Currency, related_name='transactions', on_delete=models.PROTECT)
    currency_price = models.DecimalField(max_digits=20, decimal_places=10, validators=[MinValueValidator(0)], default=0)

    commission = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    commission_currency = models.ForeignKey(Currency, related_name='transactions_commission', on_delete=models.PROTECT)

    transaction_date = models.DateTimeField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.account.name} - {self.asset.name} - {self.amount} {self.currency.code}'
    
    def clean(self):

        if self.transaction_type == 'S':
            
            assets = self.user.assets.filter(asset=self.asset, active=True)
            total_amount = assets.aggregate(Sum('amount'))['amount__sum']

            if total_amount is None or total_amount < self.amount:
                raise ValidationError('You do not have enough assets to sell.')

    def save(self, *args, **kwargs):
        import traceback
        print("################################")
        print(''.join(traceback.format_stack()))
        print("################################")

        is_new = self.pk is None
        print("is_new", is_new)

        if self.transaction_type == 'S':

            if is_new:

                self.full_clean()
                super().save(*args, **kwargs)

                UserAsset.sell_assets(self)

            else:
                raise ValidationError('Updating sell transaction will be added soon.')

        if self.transaction_type == 'B':

            if is_new:
                print("buy new")
               
                self.full_clean()
                super().save(*args, **kwargs)

                UserAsset.buy_assets(self)

            else:
                print("buy update")
                raise ValidationError('Updating buy transaction will be added soon.')
            
    def delete(self, *args, **kwargs):
        raise ValidationError('Deleting a transaction will be added soon.')



    

        
