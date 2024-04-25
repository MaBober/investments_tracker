
from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from . import Account, Wallet, Currency

def past_or_present_time(value):
    if value > timezone.now():
        raise ValidationError('Date cannot be in the future.')

class Withdrawal(models.Model):
    """
    Withdrawal model

    Attributes:
    -----

    wallet: models.ForeignKey
        The wallet the withdrawal belongs to
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
    wallet = models.ForeignKey(Wallet, related_name='withdrawals', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, related_name='withdrawals', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='withdrawals', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    currency = models.ForeignKey(Currency, related_name='withdrawals', on_delete=models.PROTECT)
    description = models.CharField(blank=True, max_length=1000)
    withdrawn_at = models.DateTimeField(validators=[past_or_present_time], null=False, blank=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.amount) + ' ' + self.currency.code+ ' ' + self.user.username
    
    def clean(self):

        if self.user != self.wallet.owner and self.user not in self.wallet.co_owners.all():
            raise ValidationError({'unauthorized_withdrawal': 'You are not authorized to make this withdrawal.'})
        
        if self.account not in self.wallet.accounts.all():
            raise ValidationError({'account_wallet_mismatch': 'The account must belong to the wallet to make a withdrawal.'})
        
        if self.user != self.account.owner and self.user not in self.account.co_owners.all():
            raise ValidationError({'unauthorized_withdrawal': 'You are not authorized to make this withdrawal.'})
        
        if self.currency not in self.account.currencies.all():
            raise ValidationError({'currency':'The currency of the withdrawal must be the same as the currency of the account.'})
        
        if self.amount is None:
            raise ValidationError({'amount':'The amount of the withdrawal cannot be empty.'})

        if self.amount > self.account.current_balance:
            raise ValidationError({'amount':'Insufficient funds to make this withdrawal.'})
        
    def save(self, *args, **kwargs):

        is_new = self.pk is None

        if is_new:

            self.full_clean()
            super().save(*args, **kwargs)

            self.account.add_withdrawal(self)

        else:
            raise ValidationError({'update_withdrawal': 'Updating withdrawals will be added soon.'})

    def delete(self, *args, **kwargs):

        self.account.remove_withdrawal(self)
        super().delete(*args, **kwargs)

