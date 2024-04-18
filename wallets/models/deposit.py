from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from . import Account, Wallet, Currency

def past_or_present_time(value):
    if value > timezone.now():
        raise ValidationError('Date cannot be in the future.')

class Deposit(models.Model):
    """
    Deposit model

    Attributes:
    -----
    wallet: models.ForeignKey
        The wallet the deposit belongs to
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
    wallet = models.ForeignKey(Wallet, related_name='deposits', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, related_name='deposits', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='deposits', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    currency = models.ForeignKey(Currency, related_name='deposits', on_delete=models.PROTECT)
    description = models.CharField(blank=True, max_length=1000)
    deposited_at = models.DateTimeField(validators=[past_or_present_time], null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.amount
    
    def clean(self):

        if self.user != self.wallet.owner and self.user not in self.wallet.co_owners.all():
            raise ValidationError('The user must be the owner or a co-owner of the wallet to make a deposit.')
        
        if self.account not in self.wallet.accounts.all():
            raise ValidationError('The account must belong to the wallet to make a deposit.')
        
        if self.user != self.account.owner and self.user not in self.account.co_owners.all():
            raise ValidationError('The user must be the owner or a co-owner of the account to make a deposit.')
    
        if self.currency != self.account.currency:
            raise ValidationError('The currency of the deposit must be the same as the currency of the account.')

    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)