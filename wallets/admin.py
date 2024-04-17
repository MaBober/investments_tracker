from django.contrib import admin

from .models import Country, Currency
from .models import Wallet, Transaction, Deposit, Withdrawal
from .models import Account, AccountInstitutionType, AccountInstitution, AccountType
from .models import AssetType, MarketAsset, MarketShare, MarketETF, AssetPrice, ExchangeMarket, AssetTypeAssociation

# Register your models here.

admin.site.register([Country, Currency])
admin.site.register([Wallet])
admin.site.register([Account, AccountInstitution, AccountInstitutionType, AccountType, ExchangeMarket])
admin.site.register([AssetType , MarketShare, MarketETF, AssetPrice, AssetTypeAssociation])
admin.site.register([Transaction, Deposit, Withdrawal])
