
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from django.db.models import Sum
from rest_framework.fields import CharField

from wallets.models import Wallet, Account, Currency, Deposit, MarketAssetTransaction, MarketAsset, Transaction, TreasuryBondsTransaction, TreasuryBonds, UserAsset, UserTreasuryBonds


class UserDetailedAssetSerializer(serializers.ModelSerializer):

    currency = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Currency.objects.all(),
        required=True,
        error_messages={
            'does_not_exist': '{value} is a wrong currency. Please provide a valid currency.'
        }
    )

    asset = serializers.SlugRelatedField(
        slug_field='code',
        queryset=MarketAsset.objects.all(),
        required=True,
        error_messages={
            'does_not_exist': '{value} is a wrong asset. Please provide a valid asset.'
        }
    )

    class Meta:
        model = UserAsset
        fields = '__all__'

    
class UserSimpleAssetSerializer(UserDetailedAssetSerializer):

    asset = serializers.SerializerMethodField()

    def get_asset(self, obj):

        asset_to_present = MarketAsset.objects.get(id=obj['asset'])
        return f'{asset_to_present.exchange_market.code}:{asset_to_present.code}'

    class Meta:
        model = UserAsset
        fields = [
            "asset",
            "amount"
        ]


class UserDetailedTreasuryBondsSerializer(serializers.ModelSerializer):

    bond = serializers.SlugRelatedField(
        slug_field='code',
        queryset=TreasuryBonds.objects.all(),
        required=True,
        error_messages={
            'does_not_exist': '{value} is a wrong treasury bond. Please provide a valid treasury bond.'
        }
    )

    class Meta:
        model = UserTreasuryBonds
        fields = '__all__'


class UserSimpleTreasuryBondsSerializer(UserDetailedTreasuryBondsSerializer):
    
        class Meta:
            model = UserTreasuryBonds
            fields = [
                "bond",
                "amount",
                "current_value"
            ]
