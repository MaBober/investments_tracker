from django.contrib import admin

from .models import Wallet, Transaction, Asset, Deposit, Withdrawal
from .models import Account, AccountInstitutionType, AccountCurrency, AccountInstitution, AccountType
# Register your models here.

admin.site.register([Wallet])
admin.site.register([Account, AccountInstitution, AccountCurrency, AccountInstitutionType, AccountType])
admin.site.register([Transaction, Asset, Deposit, Withdrawal])
