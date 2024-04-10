from django.db import models
from django.core.exceptions import ValidationError

from . import Wallet, Country, Currency
from .abstract import BaseModel, validate_name_length


class AccountType(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    description = models.CharField(blank=True, max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)
    
class AccountInstitutionType(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    description = models.CharField(blank=True, max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name  
    
    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)
    
class AccountInstitution(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    type = models.ForeignKey(AccountInstitutionType, on_delete=models.PROTECT)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    description = models.CharField(blank=True, max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)
    

class Account(BaseModel):
    """
    Account model

    Attributes:
    -----
    wallet: models.ForeignKey
        The wallet the account belongs to
    owner: models.ForeignKey
        The user who owns the account
    co_owner: models.ForeignKey
        The user who co-owns the account
    type: models.CharField
        The type of the account
    institution: models.CharField
        The institution of the account
    currency: models.CharField
        The currency of the account
    name: models.CharField
        The name of the account
    description: models.TextField
        The description of the account
    created_at: models.DateTimeField
        The date and time the account was created
    updated_at: models.DateTimeField
        The date and time the account was last updated
    current_value: models.DecimalField
        The current value of the account

    Relationships:
    -----
    wallet: Wallet
        The wallet the account belongs to
    owner: auth.User
        The user who owns the account
    co_owner: auth.User
        The user who co-owns the account

    Methods:
    -----
    __str__:
        Returns the name of the account
    
    """

    wallets = models.ManyToManyField(Wallet, related_name='accounts')
    owner = models.ForeignKey('auth.User', related_name='accounts', on_delete=models.CASCADE)
    co_owners = models.ManyToManyField('auth.User', related_name='co_owned_accounts', blank=True)
    type = models.ForeignKey(AccountType, on_delete=models.PROTECT)
    institution = models.ForeignKey(AccountInstitution, on_delete=models.PROTECT)
    other_institution = models.CharField(max_length=100, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    name = models.CharField(max_length=100, validators=[validate_name_length])
    description = models.CharField(blank=True, max_length=1000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = ['owner', 'name']

    def __str__(self):
        return self.name