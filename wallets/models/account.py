import datetime as dt

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
    

from django.db.models.signals import m2m_changed
from django.dispatch import receiver




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
    currencies: models.ManyToManyField
        The currencies of the account
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
    currencies = models.ManyToManyField(Currency, related_name='accounts', blank=True)

    name = models.CharField(max_length=100, validators=[validate_name_length])
    description = models.CharField(blank=True, max_length=1000)
    wallets = models.ManyToManyField(Wallet, related_name='accounts', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
            

    def get_balance(self, currency):
        """
        Get the balance of the account in the specified currency
        """

        balance = self.balances.filter(currency=currency).first()

        if balance:
            return balance.balance
        else:
            return 0
    
    @property
    def current_value(self):
        """
        Get the current value of the account
        """

        active_assets = self.assets.all().filter(active=True)
        active_bonds = self.bonds.all().filter(active=True)

        total_value = sum([asset.current_value for asset in active_assets])
        total_value += sum([bond.current_value for bond in active_bonds])

        return total_value
            
    def add_deposit(self, deposit):
        """
        Make a deposit to the account
        """

        if deposit.account != self:
            raise ValidationError('The deposit must be made to this account.')
        
        if deposit.currency not in self.currencies.all():
            raise ValidationError('The currency of the deposit must be the same as the currency of the account.')
        
        account_currency, created = self.balances.get_or_create(
            currency=deposit.currency,
            defaults={'balance': deposit.amount})

        if not created:

            account_currency.balance += deposit.amount
            account_currency.save()


    def remove_deposit(self, deposit):
        """
        Remove a deposit from the account
        """

        if deposit.account != self:
            raise ValidationError('The deposit must be made to this account.')
        
        if deposit.currency not in self.currencies.all():
            raise ValidationError('The currency of the deposit must be the same as the currency of the account.')


        account_currency_balance = self.balances.filter(currency=deposit.currency).first()

        if account_currency_balance:
            account_currency_balance.balance -= deposit.amount
            account_currency_balance.save()

        else:
            raise ValidationError('The account does not have a balance in the currency of the deposit.')


    def add_withdrawal(self, withdrawal):
        """
        Make a withdrawal from the account
        """

        if withdrawal.account != self:
            raise ValidationError('The withdrawal must be made from this account.')
        
        if withdrawal.currency not in self.currencies.all():
            raise ValidationError('The currency of the withdrawal must be the same as the currency of the account.')
        
        account_currency_balance = self.balances.filter(currency=withdrawal.currency).first()

        if account_currency_balance:
            account_currency_balance.balance -= withdrawal.amount
            account_currency_balance.save()
        
        else:
            raise ValidationError('The account does not have a balance in the currency of the withdrawal.')
    

    def remove_withdrawal(self, withdrawal):
        """
        Remove a withdrawal from the account
        """

        if withdrawal.account != self:
            raise ValidationError('The withdrawal must be made from this account.')
        
        if withdrawal.currency not in self.currencies.all():
            raise ValidationError('The currency of the withdrawal must be the same as the currency of the account.')
        
        account_currency_balance = self.balances.filter(currency=withdrawal.currency).first()

        if account_currency_balance:
            account_currency_balance.balance += withdrawal.amount
            account_currency_balance.save()

        else:
            raise ValidationError('The account does not have a balance in the currency of the withdrawal.')
    
    def verify_balance(self, currency):
        """
        Verify the balance of the account
        """

        deposits = self.deposits.all()
        withdrawals = self.withdrawals.all()

        total_deposits = sum([deposit.amount for deposit in deposits])
        total_withdrawals = sum([withdrawal.amount for withdrawal in withdrawals])

        total_buys = sum(
            [transaction.total_price for transaction in self.marketassettransaction.filter(transaction_type='B')] +
            [transaction.total_price for transaction in self.treasurybondstransaction.filter(transaction_type='B')]
            )
        total_sells = sum(
            [transaction.total_price for transaction in self.marketassettransaction.filter(transaction_type='S')] +
            [transaction.total_price for transaction in self.treasurybondstransaction.filter(transaction_type='S')]
            )

        current_balance = total_deposits - total_withdrawals - total_buys + total_sells

        if current_balance != self.get_balance(currency):
            raise ValidationError(f'The current balance of the account is incorrect. The current balance is {self.get_balance(currency)} but should be {current_balance}.')
        
        else:
            return True
        

    def buy_asset(self, transaction):
        """
        Buy an asset with the account
        """

        from . import UserAsset

        if transaction.account != self:
            raise ValidationError('The transaction must be made with this account.')
        
        if transaction.account_currency not in self.currencies.all():
            raise ValidationError('The currency of the transaction must be the same as the currency of the account.')
        
        if transaction.transaction_type != 'B':
            raise ValidationError('The type of the transaction must be BUY.')
    
        user_asset = UserAsset.objects.create(
            user=transaction.user,
            account=transaction.account,
            wallet=transaction.wallet,
            asset=transaction.asset,
            amount=transaction.amount,
            price=transaction.price,
            account_currency=transaction.account_currency,
            currency_price=transaction.currency_price,
            commission=transaction.commission,
            buy_transaction=transaction,
            active=True
        )
        user_asset.save()

        balance_to_update = self.balances.get(currency=transaction.account_currency)
        balance_to_update.balance -= transaction.total_price
        balance_to_update.save()

    def sell_assets(self, transaction):

        user_assets = transaction.user.assets.filter(asset=transaction.asset, account=self, active=True).order_by('created_at')

        for user_asset in user_assets:

            if user_asset.amount > transaction.amount:
                user_asset.amount -= transaction.amount
                user_asset.sell_transactions.add(transaction)
                user_asset.save()

                break
            
            elif user_asset.amount == transaction.amount:
                user_asset.active = False
                user_asset.amount = 0
                user_asset.sell_transactions.add(transaction)
                user_asset.save()
                break

            else:
                transaction.amount -= user_asset.amount
                user_asset.active = False
                user_asset.amount = 0
                user_asset.sell_transactions.add(transaction)
                user_asset.save()

        balance_to_update = self.balances.get(currency=transaction.account_currency)
        balance_to_update.balance += transaction.total_price
        balance_to_update.save()

    def buy_bond(self, transaction):
        """
        Buy a bond with the account
        """

        from . import UserTreasuryBonds

        if transaction.account != self:
            raise ValidationError('The transaction must be made with this account.')
        
        if transaction.account_currency not in self.currencies.all():
            raise ValidationError('The currency of the transaction must be the same as the currency of the account.')
        
        if transaction.transaction_type != 'B':
            raise ValidationError('The type of the transaction must be BUY.')
        
        user_bond = UserTreasuryBonds.objects.create(
            user=transaction.user,
            account=transaction.account,
            wallet=transaction.wallet,
            bond=transaction.bond,
            amount=transaction.amount,
            issue_date = transaction.transaction_date,
            maturity_date = transaction.transaction_date + transaction.bond.maturity_date_delta,
            buy_transaction=transaction,
            active=True
        )
        user_bond.save()

        balance_to_update = self.balances.get(currency=transaction.currency_price)
        balance_to_update.balance -= transaction.total_price
        balance_to_update.save()

    
    def sell_bonds(self, transaction):
        """
        Sell bonds with the account
        """

        user_bonds = transaction.user.bonds.filter(bond=transaction.bond, account=self, active=True).order_by('created_at')

        for user_bond in user_bonds:

            if user_bond.amount > transaction.amount:
                user_bond.amount -= transaction.amount
                user_bond.sell_transactions.add(transaction)
                user_bond.save()

                break
            
            elif user_bond.amount == transaction.amount:
                user_bond.active = False
                user_bond.amount = 0
                user_bond.sell_transactions.add(transaction)
                user_bond.save()
                break

            else:
                transaction.amount -= user_bond.amount
                user_bond.active = False
                user_bond.amount = 0
                user_bond.sell_transactions.add(transaction)
                user_bond.save()

        balance_to_update = self.balances.get(currency=transaction.currency)
        balance_to_update.balance += transaction.total_price
        balance_to_update.save()



@receiver(m2m_changed, sender=Account.currencies.through)
def account_currencies_changed(sender, instance, action, **kwargs):
    """
    Update the account balances when the currencies of the account are changed
    """

    if action == 'post_add':

        for currency in instance.currencies.all():
            account_currency, created = instance.balances.get_or_create(
                currency=currency,
                defaults={'balance': 0})

            # if not created:
            #     account_currency.balance = 0
            #     account_currency.save()

        # for balance in instance.balances.all():
        #     if balance.currency not in instance.currencies.all():
        #         balance.delete()


        
class AccountCurrencyBalance(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='balances')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, blank=False, null=False, default=0)

    class Meta:
        unique_together = ['account', 'currency']

    def __str__(self):
        return f'{self.account.name} - {self.currency.code} - {self.balance}'