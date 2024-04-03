from django.contrib.auth.models import User

from rest_framework import serializers

from .models import Wallet

class UserSerializer(serializers.ModelSerializer):
    
    wallets = serializers.PrimaryKeyRelatedField(many=True, queryset=Wallet.objects.all())
    co_owned_wallets = serializers.PrimaryKeyRelatedField(many=True, queryset=Wallet.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'wallets', 'co_owned_wallets']


class WalletSerializer(serializers.ModelSerializer):
    """
    Wallet serializer
    """
    owner = UserSerializer(many=False, read_only=True)
    co_owner = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'owner', 'co_owner', 'name', 'description', 'created_at', 'updated_at']

