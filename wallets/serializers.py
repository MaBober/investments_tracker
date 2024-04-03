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


class WalletCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Wallet model instance.

    This serializer is used to convert JSON data into a Wallet model instance.

    Attributes:
        owner: A PrimaryKeyRelatedField that represents the owner of the wallet.
        co_owner: A PrimaryKeyRelatedField that represents the co-owner of the wallet.
    
    Methods:
        validate_co_owner: A method that validates the co_owner field.
            It checks if the owner is not in the co_owner list.
        validate_name: A method that validates the name field.
            It checks if the name is at least 3 characters long and if a wallet with this name already exists.
    """

    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    co_owner = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Wallet
        fields = ['id', 'owner', 'co_owner', 'name', 'description']


    def validate_co_owner(self, value):

        owner = self.context['request'].user
        
        if owner in value:
            raise serializers.ValidationError("Owner cannot be a co-owner")
        return value
    
    def validate_name(self, value):

        owner = self.context['request'].user

        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long")
        
        if Wallet.objects.filter(owner=owner, name=value).exists():
            raise serializers.ValidationError("Wallet with this name already exists")
        return value

    

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
    co_owner = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'owner', 'co_owner', 'name', 'description', 'created_at', 'updated_at']

