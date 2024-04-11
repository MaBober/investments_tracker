from django.db import models
from django.core.exceptions import ValidationError

from . import Account

class Deposit(models.Model):
    """
    Deposit model

    Attributes:
    -----
    account: models.ForeignKey
        The account the deposit belongs to
    user: models.ForeignKey
        The user who made the deposit
    amount: models.DecimalField
        The amount of the deposit
    currency: models.CharField
        The currency of the deposit
    description: models.TextField
        The description of the deposit
    deopsited_at: models.DateTimeField
        The date and time the deposit was made
    created_at: models.DateTimeField
        The date and time the deposit was created
    updated_at: models.DateTimeField
        The date and time the deposit was last updated
    
    Relationships:
    -----
    account: Account
        The account the deposit belongs to
    user: auth.User
        The user who made the deposit

    Methods:
    -----
    __str__:
        Returns the amount of the deposit
    
    """
    account = models.ForeignKey(Account, related_name='deposits', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='deposits', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    deposited_at = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.amount