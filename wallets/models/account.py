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

    owner = models.ForeignKey('auth.User', related_name='accounts', on_delete=models.CASCADE)
    co_owners = models.ManyToManyField('auth.User', related_name='co_owned_accounts', blank=True)

    type = models.ForeignKey(AccountType, on_delete=models.PROTECT)
    institution = models.ForeignKey(AccountInstitution, on_delete=models.PROTECT)
    other_institution = models.CharField(max_length=100, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)

    name = models.CharField(max_length=100, validators=[validate_name_length])
    description = models.CharField(blank=True, max_length=1000)
    wallets = models.ManyToManyField(Wallet, related_name='accounts', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, blank=False, null=False, default=0)

    class Meta:
        unique_together = ['owner', 'name']

    def __str__(self):
        return self.name
    
    def clean(self):
        
        super().clean()

        if hasattr(self, 'institution'):
            if self.institution.name != 'Other' and (self.other_institution or self.other_institution != ''):
                raise ValidationError('Other institution field must be blank if institution is selected.')
            
            if self.institution.name == 'Other' and (not self.other_institution or self.other_institution == ''):
                raise ValidationError('Other institution field must not be blank if Other institution is selected.')
            
    def add_deposit(self, deposit):
        """
        Make a deposit to the account
        """

        if deposit.account != self:
            raise ValidationError('The deposit must be made to this account.')
        
        if deposit.currency != self.currency:
            raise ValidationError('The currency of the deposit must be the same as the currency of the account.')

        self.current_balance += deposit.amount
        self.save()

    def remove_deposit(self, deposit):
        """
        Remove a deposit from the account
        """

        if deposit.account != self:
            raise ValidationError('The deposit must be made to this account.')
        
        if deposit.currency != self.currency:
            raise ValidationError('The currency of the deposit must be the same as the currency of the account.')

        self.current_balance -= deposit.amount
        self.save()

    
    def verify_balance(self):
        """
        Verify the balance of the account
        """

        deposits = self.deposits.all()
        withdrawals = self.withdrawals.all()

        total_deposits = sum([deposit.amount for deposit in deposits])
        total_withdrawals = sum([withdrawal.amount for withdrawal in withdrawals])

        current_balance = total_deposits - total_withdrawals

        if current_balance != self.current_balance:
            raise ValidationError(f'The current balance of the account is incorrect. The current balance is {self.current_balance} but should be {current_balance}.')
        
        else:
            return True
        

    def buy_asset(self, transaction):
        """
        Buy an asset with the account
        """

        from . import UserAsset

        if transaction.account != self:
            raise ValidationError('The transaction must be made with this account.')
        
        if transaction.currency != self.currency:
            raise ValidationError('The currency of the transaction must be the same as the currency of the account.')
        
        if transaction.type != 'BUY':
            raise ValidationError('The type of the transaction must be BUY.')
    
        if transaction.total_price > self.current_balance:
            raise ValidationError('The account does not have enough balance to make the transaction.')

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


    def sell_asset(self, transaction):

        user_assets = transaction.user.assets.objects.filter(asset=transaction.asset, account=self, active=True).order_by('created_at')

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
        



            
    