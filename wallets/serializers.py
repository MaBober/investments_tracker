from django.contrib.auth.models import User

from rest_framework import serializers

from .models import Wallet

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer is used to convert User model instances into JSON
    representations and vice versa. It specifies the fields that should be
    included in the serialized output.

    Attributes:
        wallets: A PrimaryKeyRelatedField that represents the wallets owned by the user.
        co_owned_wallets: A PrimaryKeyRelatedField that represents the wallets co-owned by the user.

    """

    wallets = serializers.PrimaryKeyRelatedField(many=True, queryset=Wallet.objects.all())
    co_owned_wallets = serializers.PrimaryKeyRelatedField(many=True, queryset=Wallet.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'wallets', 'co_owned_wallets']


class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer for the Wallet model.

    This serializer is used to convert Wallet model instances into JSON
    representations and vice versa. It specifies the fields that should be
    included in the serialized output.

    Attributes:
        owner: A UserSerializer instance that represents the owner of the wallet.
        co_owner: A UserSerializer instance that represents the co-owner of the wallet.
    """
    owner = UserSerializer(many=False, read_only=True)
    co_owner = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'owner', 'co_owner', 'name', 'description', 'created_at', 'updated_at']

