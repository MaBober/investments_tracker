from django.db import models
from django.core.exceptions import ValidationError


def validate_name_length(value):
    if len(value) < 3:
        raise ValidationError('Name must be at least 3 characters long')

class Wallet(models.Model):
    """
    Wallet model

    Attributes:
    -----
    owner: models.ForeignKey
        The user who owns the wallet
    co_owners: models.ManyToManyField
        The user who co-owns the wallet
    name: models.CharField
        The name of the wallet
    description: models.TextField
        The description of the wallet
    created_at: models.DateTimeField
        The date and time the wallet was created
    updated_at: models.DateTimeField
        The date and time the wallet was last updated

    Relationships:
    -----
    owner: auth.User
        The user who owns the wallet
    co_owner: auth.User
        The user who co-owns the wallet

    Methods:
    -----
    __str__:
        Returns the name of the wallet
    clean:
        Validates the wallet
    save:
        
    """
    owner = models.ForeignKey('auth.User', related_name='wallets', on_delete=models.CASCADE, null=False)
    co_owners = models.ManyToManyField('auth.User', related_name='co_owned_wallets', blank=True)
    name = models.CharField(max_length=100, validators=[validate_name_length])
    description = models.CharField(blank=True, max_length=1000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['owner', 'name']

    def __str__(self):
        return self.name
    
    def clean(self):
  
        if self.id:
            if self.owner and self.co_owners.filter(id=self.owner.id).exists():
                raise ValidationError('The owner and co-owner must be different users')
        
    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)
    

class Account(models.Model):
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

    wallet = models.ManyToManyField(Wallet, related_name='accounts')
    owner = models.ForeignKey('auth.User', related_name='accounts', on_delete=models.CASCADE)
    co_owner = models.ManyToManyField('auth.User', related_name='co_owned_accounts', blank=True)
    type = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    currency = models.CharField(max_length=100, default='PLN')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_value = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.name
    
    
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
    

class Transaction(models.Model):
    """
    Transaction model

    Attributes:
    -----
    asset: models.ForeignKey
        The asset bought in the transaction
    account: models.ForeignKey
        The account with which the transaction is associated
    type: models.CharField
        The type of the bought asset
    quantity: models.DecimalField
        The quantity of the bought asset
    price: models.DecimalField
        The price of the bought asset
    currency: models.CharField
        The currency of the bought asset
    commission: models.DecimalField
        The commission of the transaction
    commission_currency: models.CharField
        The currency of the commission
    description: models.TextField
        The description of the transaction
    bought_at: models.DateTimeField
        The date and time the asset was bought
    created_at: models.DateTimeField
        The date and time the transaction was created
    updated_at: models.DateTimeField
        The date and time the transaction was last updated
    
    Relationships:
    -----
    asset: Asset
        The asset bought in the transaction
    account: Account
        The account with which the transaction is associated
    
    Methods:
    -----
    __str__:
        Returns the type of the bought asset
    
    """
    asset = models.ForeignKey(Asset, related_name='transactions', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, related_name='transactions', on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=100, default='PLN')
    commission = models.DecimalField(max_digits=12, decimal_places=2)
    commission_currency = models.CharField(max_length=100, default='PLN')
    description = models.TextField(blank=True)
    bought_at = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type

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





    



