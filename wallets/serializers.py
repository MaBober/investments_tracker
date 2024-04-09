from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.fields import CharField

from .models import Wallet, Account

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
        owner_id: A PrimaryKeyRelatedField that represents the owner of the wallet.
        co_owners: A PrimaryKeyRelatedField that represents the co-owner of the wallet.
    
    Methods:
        validate_co_owners: A method that validates the co_owner field.
            It checks if the owner is not in the co_owner list.
        validate_name: A method that validates the name field.
            It checks if the name is at least 3 characters long and if a wallet with this name already exists.
    """

    owner_id = serializers.PrimaryKeyRelatedField(read_only=True)
    co_owners = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)

    class Meta:
        model = Wallet
        fields = ['id', 'owner_id', 'co_owners', 'name', 'description']


    def validate_co_owners(self, value):

        owner = self.instance.owner if self.instance else self.context['request'].user

        if owner in value:
            raise serializers.ValidationError("Owner cannot be a co-owner of the wallet.")
        return value
    
    def validate_name(self, value):

        owner = self.context['request'].user

        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long")
        
        existing_wallet = Wallet.objects.filter(owner=owner, name=value).first()
        if existing_wallet and (self.instance is None or existing_wallet.id != self.instance.id):
            raise serializers.ValidationError("Wallet with this Owner and Name already exists.")

        return value
    

class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer for the Wallet model.

    This serializer is used to convert Wallet model instances into JSON
    representations and vice versa. It specifies the fields that should be
    included in the serialized output.

    Attributes:
        owner_id: A UserSerializer instance that represents the owner of the wallet.
        co_owners: A UserSerializer instance that represents the co-owner of the wallet.
    """
    owner_id = CharField(source='owner.id', read_only=True)
    co_owners = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)

    class Meta:
        model = Wallet
        fields = ['id', 'owner_id', 'co_owners', 'name', 'description', 'created_at', 'updated_at']








class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for the Account model.

    This serializer is used to convert Account model instances into JSON
    representations and vice versa. It specifies the fields that should be
    included in the serialized output.

    Attributes:
        wallet_id: A PrimaryKeyRelatedField that represents the wallet associated with the account.
    """

    owner_id = CharField(source='owner.id', read_only=True)
    wallets_id = serializers.PrimaryKeyRelatedField(many=True, queryset=Wallet.objects.all(), required=False)
    

    class Meta:
        model = Account
        fields = ['id', 'name', 'wallets_id', 'owner_id', 'type', 'institution', 'description', 'currency', 'created_at', 'updated_at']


class AccountCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating an Account model instance.

    This serializer is used to convert JSON data into an Account model instance.

    Attributes:
        wallet_id: A PrimaryKeyRelatedField that represents the wallet associated with the account.
    """

    owner_id = serializers.PrimaryKeyRelatedField(read_only=True)
    wallets = serializers.PrimaryKeyRelatedField(many=True, queryset=Wallet.objects.all(), required=False)
    co_owners = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)

    class Meta:
        model = Account
        fields = ['id', 'owner_id', 'co_owners', 'name', 'wallets', 'type', 'institution', 'description', 'currency']

    def validate_wallets(self, value):

        owner = self.context['request'].user

        for wallet in value:
            if wallet.owner != owner:
                raise serializers.ValidationError("You do not have permission to create an account for this wallet.")
        
        return value
    
    def validate_co_owners(self, value):

        owner = self.instance.owner if self.instance else self.context['request'].user

        if owner in value:
            raise serializers.ValidationError("Owner cannot be a co-owner of the wallet.")
        return value
    
    def validate_name(self, value):
            
        owner = self.context['request'].user

        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long")

        if Account.objects.filter(owner=owner, name=value).exists():
            raise serializers.ValidationError("Account with this Owner and Name already exists.")
        
        return value
    
    #TODO: Add validation for type, institution, and currency
    def validate_type(self, value):
        return value
    
    def validate_institution(self, value):
        return value
    
    def validate_currency(self, value):
        return value
    
    def validate_description(self, value):
        
        if len(value) > 1000:
            raise serializers.ValidationError("Description must be less than 1000 characters long.")
        return value