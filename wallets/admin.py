from django.contrib import admin

from .models import Country, Currency
from .models import Wallet, Transaction, Deposit, Withdrawal
from .models import Account, AccountInstitutionType, AccountInstitution, AccountType
from .models import AssetType, MarketAsset, MarketShare, MarketETF, AssetPrice, ExchangeMarket, AssetTypeAssociation
from .models import Deposit

# Register your models here.

admin.site.register([Country, Currency])
admin.site.register([Wallet])
admin.site.register([Account, AccountInstitution, AccountInstitutionType, AccountType, ExchangeMarket])
admin.site.register([AssetType , MarketShare, MarketETF, AssetPrice, AssetTypeAssociation])
admin.site.register([Deposit])
admin.site.register([Withdrawal])

@admin.register(Transaction)
class Transaction(admin.ModelAdmin):
    fields =['user', 'transaction_type', ('wallet', 'account'),'asset', 'amount', ('price', 'currency'),'currency_price',('commission','commission_currency'), 'transaction_date']


