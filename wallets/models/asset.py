from django.db import models
from django.core.exceptions import ValidationError

from . import Account

class Asset(models.Model):
    """
    Asset model

    Attributes:
    -----
    account: models.ForeignKey
        The account the asset belongs to
    type: models.CharField
        The type of the asset
    symbol: models.CharField
        The symbol of the asset
    name: models.CharField
        The name of the asset
    description: models.TextField
        The description of the asset
    price: models.DecimalField
        The price of the asset
    quantity: models.DecimalField
        The quantity of the asset
    currency: models.CharField
        The currency of the asset
    currency_exchange_rate: models.DecimalField
        The currency exchange rate of the asset
    commission: models.DecimalField
        The commission of the asset
    commission_currency: models.CharField
        The currency of the commission
    bought_at: models.DateTimeField
        The date and time the asset was bought
    created_at: models.DateTimeField
        The date and time the asset was created
    updated_at: models.DateTimeField
        The date and time the asset was last updated
    
    Relationships:
    -----
    account: Account
        The account the asset belongs to
    
    Methods:
    -----
    __str__:
        Returns the name of the asset
    
    """
    account = models.ForeignKey(Account, related_name='assets', on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=100, default='PLN')
    currency_exchange_rate = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2)
    commission_currency = models.CharField(max_length=100, default='PLN')
    bought_at = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name