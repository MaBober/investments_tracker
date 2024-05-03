from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from django.db.models import Sum
from rest_framework.fields import CharField

from wallets.models import Wallet, Account, Currency, Deposit, MarketAssetTransaction, MarketAsset, Transaction, TreasuryBondsTransaction, TreasuryBonds

class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transaction model.

    This serializer is used to convert Transaction model instances into JSON
    representations and vice versa. It specifies the fields that should be
    included in the serialized output.

    Attributes:
        account_id: A PrimaryKeyRelatedField that represents the account associated with the transaction.
    """

    account_id = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())

    class Meta:
       # model = Transaction
        fields = [
            'id',
            'user_id',
            'transaction_type',
            'account_id',
            'wallet_id',
            'amount',
            'price',
            'currency',
            'currency_price',
            'commission',
            'commission_currency',
            'transaction_date',
            'total_price'
        ]
        abstract = True

class TransactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Transaction model instance.

    This serializer is used to convert JSON data into a Transaction model instance.

    Attributes:
        account_id: A PrimaryKeyRelatedField that represents the account associated with the transaction.
    """

    user_id = serializers.PrimaryKeyRelatedField(read_only=True)
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())

    code = serializers.CharField(max_length=10, required=True, write_only=True)
    exchange_market = serializers.CharField(required=True, write_only=True)

    currency = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Currency.objects.all(),
        required=True,
        error_messages={
            'does_not_exist': '{value} is a wrong currency. Please provide a valid currency.'
        }
    )
    currency_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    commission = serializers.DecimalField(max_digits=12, decimal_places=2, required=True, min_value=0)
    commission_currency = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Currency.objects.all(),
        required=True,
        error_messages={
            'does_not_exist': '{value} is a wrong currency. Please provide a valid currency.'
        }
    )

    class Meta:
        # model = Transaction
        fields = ['id', 'user_id', 'account', 'wallet', 'transaction_type', 'amount', 'price', 'currency','currency_price', 'commission', 'commission_currency',  'transaction_date']
        abstract = True


    def validate_wallet(self, value):

        if value.owner != self.context['request'].user and self.context['request'].user not in value.co_owners.all():
            raise serializers.ValidationError('You do not own this wallet.')

        return value
    
    def validate_account(self, value):

        if value.owner != self.context['request'].user and self.context['request'].user not in value.co_owners.all():
            raise serializers.ValidationError('You do not own this account.')

        return value
    
    def validate_currency(self, value):

        account_id = self.initial_data.get('account')
        try:
            account = Account.objects.get(pk=account_id)
        except ObjectDoesNotExist:
            return value

        if value not in account.currencies.all():
            raise serializers.ValidationError('This currency is not supported by this account.')
        
        return value
        
    

    
    def validate(self, data):

        wallet = data.get('wallet')
        account = data.get('account')
        currency = Currency.objects.get(code=self.initial_data.get('currency'))

        if wallet and account:
            if not wallet.accounts.filter(pk=account.pk).exists():
                raise serializers.ValidationError({'account_wallet_mismatch': 'The account must belong to the wallet to make a transaction.'})
            
            total_price = self.calculate_total_price()

            if total_price > account.get_balance(currency):
                raise serializers.ValidationError({"not_enough_funds":'Insufficient funds in the account.'})
            if total_price == -1:
                raise serializers.ValidationError({'error': 'An error occurred while calculating the total price. Verify data.'})

        return data

    def calculate_total_price(self):

        try:

            transaction_type = self.initial_data.get('transaction_type')
            amount = float(self.initial_data.get('amount'))
            price = float(self.initial_data.get('price'))
            currency = self.initial_data.get('currency')
            currency_price = float(self.initial_data.get('currency_price'))
            commission = float(self.initial_data.get('commission'))
            commission_currency = self.initial_data.get('commission_currency')
        

            account = Account.objects.get(pk=self.initial_data.get('account'))

            if transaction_type == 'B':

                price_in_asset_currency = amount * price

                if currency not in account.currencies.all():
                    price_in_account_currency = price_in_asset_currency * currency_price
                else:
                    price_in_account_currency = price_in_asset_currency

                if commission_currency in account.currencies.all():
                    commission = commission
                else:
                    pass

                return price_in_account_currency + commission
            
            if transaction_type == 'S':

                return 0

                # price_in_asset_currency = amount * price

                # if currency not in account.currencies.all():
                #     price_in_account_currency = price_in_asset_currency * currency_price
                # else:
                #     price_in_account_currency = price_in_asset_currency

                # if commission_currency in account.currencies.all():
                #     commission = commission
                # else:
                #     pass

                # return price_in_account_currency - commission
            else:
                return -1
            
        except:
            return -1    
        
    
    



class MarketAssetTransactionSerializer(TransactionSerializer):
    """
    Serializer for the MarketAssetTransaction model.

    This serializer is used to convert MarketAssetTransaction model instances into JSON
    representations and vice versa. It specifies the fields that should be
    included in the serialized output.
    """

    class Meta:
        model = MarketAssetTransaction
        market_asset_fields = TransactionSerializer.Meta.fields.copy()
        market_asset_fields.append('asset')
        fields = market_asset_fields

class MarketAssetTransactionCreateSerializer(TransactionCreateSerializer):
    """
    Serializer for creating a MarketAssetTransaction model instance.

    This serializer is used to convert JSON data into a MarketAssetTransaction model instance.
    """

    asset_code = serializers.SerializerMethodField()

    class Meta:
        model = MarketAssetTransaction
        market_asset_fields = TransactionCreateSerializer.Meta.fields.copy()
        market_asset_fields.extend(['code', 'exchange_market', 'asset_code'])

        fields = market_asset_fields

        extra_kwargs = {
        'code': {'write_only': True},
        'exchange_market': {'write_only': True},
        'asset' : {'read_only': True,'required': False}
        }

    def get_asset_code(self, obj):
        return obj.asset.code
    

    def validate(self, data):

        super().validate(data)

        code = data.get('code')
        exchange_market = data.get('exchange_market')
        user = self.context['request'].user
        account = data.get('account')

        if not code:
            raise serializers.ValidationError('Asset code is required.')
        if not exchange_market:
            raise serializers.ValidationError('Exchange market is required.')
        
        try:
            asset = MarketAsset.objects.get(code=code, exchange_market=exchange_market)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Asset does not exist.')
        
        if data.get('transaction_type') == 'S':
        
            assets = user.assets.filter(asset=asset, active=True, account=account)
            total_amount = assets.aggregate(Sum('amount'))['amount__sum']

            if total_amount is None or total_amount < data.get('amount'):
                raise serializers.ValidationError({"amount":'You do not have enough assets to sell.'})
        
        data.pop('code', None)
        data.pop('exchange_market', None)

        data['asset'] = asset

        return data


class TreasuryBondsTransactionSerializer(TransactionSerializer):
    """
    Serializer for the TreasuryBondsTransaction model.

    This serializer is used to convert TreasuryBondsTransaction model instances into JSON
    representations and vice versa. It specifies the fields that should be
    included in the serialized output.
    """

    class Meta:
        model = TreasuryBondsTransaction

        bond_fields = TransactionSerializer.Meta.fields.copy()
  

        fields = bond_fields

class TreasuryBondsTransactionCreateSerializer(TransactionCreateSerializer):
    """
    Serializer for creating a TreasuryBondsTransaction model instance.
    
    This serializer is used to convert JSON data into a TreasuryBondsTransaction model instance.
    """
    bond = serializers.SlugRelatedField(
        slug_field='code',
        queryset=TreasuryBonds.objects.all(),
        required=True,
        error_messages={
            'does_not_exist': '{value} is a wrong bond. Please provide a valid bond.'
        }
    )

    class Meta:
        model = TreasuryBondsTransaction

        bond_fields = TransactionCreateSerializer.Meta.fields
        bond_fields.extend(['bond'])
        
        fields = bond_fields

