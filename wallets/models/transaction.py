from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from . import  Account, Wallet, Currency, MarketAsset

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
    commission_currency_price = models.DecimalField(max_digits=20, decimal_places=10, validators=[MinValueValidator(0)], default=0)

    transaction_date = models.DateTimeField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):  
        if self.transaction_type == 'B':

            price_in_asset_currency = self.amount * self.price

            if self.currency not in self.account.currencies.all():
                price_in_account_currency = price_in_asset_currency * self.currency_price
            else:
                price_in_account_currency = price_in_asset_currency

            if self.commission_currency in self.account.currencies.all():
                commission = self.commission
            else:
                commission = self.commission * self.commission_currency_price

            return price_in_account_currency + commission
        
        if self.transaction_type == 'S':

            price_in_asset_currency = self.amount * self.price

            if self.currency not in self.account.currencies.all():
                price_in_account_currency = price_in_asset_currency * self.currency_price
            else:
                price_in_account_currency = price_in_asset_currency

            if self.commission_currency in self.account.currencies.all():
                commission = self.commission
            else:
                commission = self.commission * self.commission_currency_price

            return price_in_account_currency - commission

    def __str__(self):
        return f'{self.account.name} - {self.asset.name} - {self.amount} {self.currency.code}'
    
    def clean(self):

        if self.transaction_type == 'S':
            
            assets = self.user.assets.filter(asset=self.asset, active=True)
            total_amount = assets.aggregate(Sum('amount'))['amount__sum']

            if total_amount is None or total_amount < self.amount:
                raise ValidationError('You do not have enough assets to sell.')

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        if self.transaction_type == 'S':

            if is_new:

                self.full_clean()
                super().save(*args, **kwargs)
                self.account.sell_assets(self)

            else:
                raise ValidationError('Updating sell transaction will be added soon.')

        if self.transaction_type == 'B':

            if is_new:
               
                self.full_clean()
                super().save(*args, **kwargs)

                self.account.buy_asset(self)

            else:
                raise ValidationError('Updating buy transaction will be added soon.')
            
    def delete(self, *args, **kwargs):
        raise ValidationError('Deleting a transaction will be added soon.')
    