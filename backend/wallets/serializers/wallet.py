from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.fields import CharField

from wallets.models import Wallet
from wallets.serializers.assets import UserSimpleTreasuryBondsSerializer
from wallets.serializers.generic import CommaSeparatedIntegerListField


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
    current_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'owner_id', 'co_owners', 'name', 'description', 'created_at', 'updated_at', 'current_value',]



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
        fields = ['id','name', 'owner_id', 'co_owners', 'description']


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
    

class WalletListParametersSerializer(serializers.Serializer):
    """
    Serializer for the Wallet list filtring parameters.

    This serializer is used to validate the query parameters for the Wallet list view.

    Attributes:
        owner_id: A CommaSeparatedIntegerListField that represents the owners ids.
        co_owner_id: A CommaSeparatedIntegerListField that represents the co-owners ids.
        created_before: A DateTimeField that represents the date before which the wallets were created.
        created_after: A DateTimeField that represents the date after which the wallets were created.

    """

    owner_id = CommaSeparatedIntegerListField(child=serializers.IntegerField(), required=False)
    co_owner_id = CommaSeparatedIntegerListField(child=serializers.IntegerField(), required=False)
    created_before = serializers.DateTimeField(required=False)
    created_after = serializers.DateTimeField(required=False)
    

