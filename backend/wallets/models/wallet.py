from django.db import models
from django.core.exceptions import ValidationError

from . import BaseModel, validate_name_length


class Wallet(BaseModel):
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
    description: models.CharField
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
    
    @property
    def current_value(self):
        """
        Get the current value of the account
        """

        active_assets = self.assets.all().filter(active=True)
        active_bonds = self.bonds.all().filter(active=True)

        total_value_assets = sum([asset.current_value for asset in active_assets])
        total_value_bonds = sum([bond.current_value for bond in active_bonds])

        total_value = total_value_assets + total_value_bonds

        wallet_proportion = {
            'assets': (total_value_assets/total_value) if total_value != 0 else 0,
            'bonds': (total_value_bonds/total_value) if total_value != 0 else 0
        }

        return round(total_value,2)
    
    @property
    def wallet_proportion(self):
        """
        Get the proportion of the wallet value that is in assets and bonds
        """


        active_assets = self.assets.all().filter(active=True)
        active_bonds = self.bonds.all().filter(active=True)

        total_value_assets = sum([asset.current_value for asset in active_assets])
        total_value_bonds = sum([bond.current_value for bond in active_bonds])

        total_value = total_value_assets + total_value_bonds

        wallet_proportion = {
            'assets': ((total_value_assets/total_value) if total_value != 0 else 0, total_value_assets),
            'bonds': ((total_value_bonds/total_value) if total_value != 0 else 0, total_value_bonds)
        }

        return wallet_proportion
    
    @property
    def cash_balance(self):
        """
        Get the cash balance of the account
        """

        deposits = self.deposits.all()
        withdrawals = self.withdrawals.all()

        total_deposits = sum([deposit.amount for deposit in deposits])
        total_withdrawals = sum([withdrawal.amount for withdrawal in withdrawals])

        return total_deposits - total_withdrawals

