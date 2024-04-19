from django.db import models
from django.core.exceptions import ValidationError

from . import Account

class Withdrawal(models.Model):
    """
    Withdrawal model

    Attributes:
    -----
    account: models.ForeignKey
        The account the withdrawal belongs to
    user: models.ForeignKey
        The user who made the withdrawal
    amount: models.DecimalField
        The amount of the withdrawal
    currency: models.CharField
        The currency of the withdrawal
    description: models.TextField
        The description of the withdrawal
    withdrawn_at: models.DateTimeField
        The date and time the withdrawal was made
    created_at: models.DateTimeField
        The date and time the withdrawal was created
    updated_at: models.DateTimeField
        The date and time the withdrawal was last updated
    
    Relationships:
    -----
    account: Account
        The account the withdrawal belongs to
    user: auth.User
        The user who made the withdrawal

    Methods:
    -----
    __str__:
        Returns the amount of the withdrawal
    
    """
    account = models.ForeignKey(Account, related_name='withdrawals', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='withdrawals', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    withdrawn_at = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.amount

