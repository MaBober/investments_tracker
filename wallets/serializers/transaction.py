from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from rest_framework.fields import CharField

from wallets.models import Wallet, Account, Currency, Deposit, Transaction, MarketAsset

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
        model = Transaction
        fields = [
            'id',
            'user_id',
            'transaction_type',
            'account_id',
            'wallet_id',
            'asset',
            'amount',
            'price',
            'currency',
            'currency_price',
            'commission',
            'commission_currency',
            'transaction_date',
        ]

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
    commission = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    commission_currency = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Currency.objects.all(),
        required=False,
        error_messages={
            'does_not_exist': '{value} is a wrong currency. Please provide a valid currency.'
        }
    )
    transaction_date = serializers.DateTimeField(required=True)


    class Meta:
        model = Transaction
        fields = ['id', 'user_id', 'account','wallet', 'code', 'exchange_market', 'transaction_type', 'amount', 'price', 'currency','currency_price', 'commission', 'commission_currency',  'transaction_date']
        extra_kwargs = {
        'code': {'write_only': True},
        'exchange_market': {'write_only': True},
        }

    def validate(self, data):

        code = data.get('code')
        exchange_market = data.get('exchange_market')

        if not code:
            raise serializers.ValidationError('Asset code is required.')
        if not exchange_market:
            raise serializers.ValidationError('Exchange market is required.')
        
        try:
            asset = MarketAsset.objects.get(code=code, exchange_market=exchange_market)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Asset does not exist.')
        
        data.pop('code', None)
        data.pop('exchange_market', None)

        data['asset'] = asset

        return data

    # def to_internal_value(self, data):


        
    #     print(asset)
        
    #     data['asset'] = asset
    #     print(f'Before pop: {data}')

    #     print(f'After pop: {data}')




    #     return super().to_internal_value(data)