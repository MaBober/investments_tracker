from django.contrib import admin

from .models import Wallet, Account, Transaction, Asset, Deposit, Withdrawal

# Register your models here.

admin.site.register([Wallet, Account, Transaction, Asset, Deposit, Withdrawal])