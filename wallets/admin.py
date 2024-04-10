from django.contrib import admin

from .models import Country, Currency
from .models import Wallet, Transaction, Asset, Deposit, Withdrawal
from .models import Account, AccountInstitutionType, AccountInstitution, AccountType

# Register your models here.

admin.site.register([Country, Currency])
admin.site.register([Wallet])
admin.site.register([Account, AccountInstitution, AccountInstitutionType, AccountType])
admin.site.register([Transaction, Asset, Deposit, Withdrawal])
