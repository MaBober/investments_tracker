from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


from rest_framework import serializers
from rest_framework.fields import CharField

from wallets.models import Wallet, Account, Currency, Deposit

class DepositSerializer(serializers.ModelSerializer):
    """
    Serializer for the Deposit model.

    This serializer is used to convert Deposit model instances into JSON
    representations and vice versa. It specifies the fields that should be
    included in the serialized output.

    Attributes:
        wallet_id: A PrimaryKeyRelatedField that represents the wallet associated with the deposit.
        account_id: A PrimaryKeyRelatedField that represents the account associated with the deposit.
        user_id: A PrimaryKeyRelatedField that represents the user associated with the deposit.
    """

    wallet_id = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())
    account_id = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    currency = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Currency.objects.all()
    )

    class Meta:
        model = Deposit
        fields = ['id', 'wallet_id', 'account_id', 'user_id', 'amount', 'currency', 'description', 'deposited_at', 'created_at', 'updated_at']


class DepositCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Deposit model instance.

    This serializer is used to convert JSON data into a Deposit model instance.

    Attributes:
        wallet_id: A PrimaryKeyRelatedField that represents the wallet associated with the deposit.
        account_id: A PrimaryKeyRelatedField that represents the account associated with the deposit.
        user_id: A PrimaryKeyRelatedField that represents the user associated with the deposit.
    """

    user_id = serializers.PrimaryKeyRelatedField(read_only=True)
    wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())

    currency = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Currency.objects.all(),
        required=True,
        error_messages={
            'does_not_exist': '{value} is a wrong currency. Please provide a valid currency.'
        }
    )


    class Meta:
        model = Deposit
        fields = ['id', 'wallet', 'account', 'user_id', 'amount', 'currency', 'description', 'deposited_at']

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
            account = Account.objects.first()
        except ObjectDoesNotExist:
            return value

        if value not in account.currencies.all():
            raise serializers.ValidationError('This currency is not supported by this account.')
        
        return value
    

    def validate(self, data):

        wallet = data.get('wallet')
        account = data.get('account')

        if wallet and account:
            if not wallet.accounts.filter(pk=account.pk).exists():
                raise serializers.ValidationError({'account_wallet_mismatch': 'The account must belong to the wallet to make a deposit.'})

        return data