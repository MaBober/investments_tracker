from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.fields import CharField

from wallets.models import Wallet, Account, AccountInstitution, AccountInstitutionType, AccountType, Currency


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
    wallets = serializers.PrimaryKeyRelatedField(many=True, queryset=Wallet.objects.all())

    type = serializers.SlugRelatedField(
        slug_field='name',
        queryset=AccountType.objects.all()
    )
    institution = serializers.SlugRelatedField(
        slug_field='name',
        queryset=AccountInstitution.objects.all()
    )
    currency = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Currency.objects.all()
    )
    

    class Meta:
        model = Account
        fields = ['id', 'owner_id', 'name', 'wallets', 'type', 'institution', 'description', 'currency', 'created_at', 'updated_at']


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
    type = serializers.SlugRelatedField(
        slug_field='name',
        queryset=AccountType.objects.all(),
        error_messages={
            'does_not_exist': '{value} is a wrong account type. Please provide a valid account type.'
        },
    )
    institution = serializers.SlugRelatedField(
        slug_field='name',
        queryset=AccountInstitution.objects.all(),
        error_messages={
            'does_not_exist': '{value} is a wrong institution. Please provide a valid account institution.'
        },
        required=True
    )
    other_institution = serializers.CharField(max_length=100, required=False, allow_blank=True)
    currency = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Currency.objects.all(),
        error_messages={
            'does_not_exist': 'Currency with short name {value} does not exist.'
        },
        required=True
    )
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True)

    class Meta:
        model = Account
        fields = ['id', 'owner_id', 'co_owners', 'name', 'wallets', 'other_institution', 'type', 'institution', 'description', 'currency']

    def validate(self, data):
        institution = data.get('institution').name.strip().lower()
        other_institution = data.get('other_institution')

        if institution == 'other' and (not other_institution or other_institution == ''):
            raise serializers.ValidationError({
                'other_institution': 'This field cannot be empty if institution is set to "Other".'
        })

        if institution != 'other' and other_institution and other_institution != '':
            raise serializers.ValidationError({
                'other_institution': "This field must be empty if institution is not set to 'Other'."
        })
        return data

    def validate_wallets(self, value):

        owner = self.context['request'].user

        for wallet in value:
            if wallet.owner != owner and owner not in wallet.co_owners.all():
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
        
        existing_account = Account.objects.filter(owner=owner, name=value).first()
        if existing_account and (self.instance is None or existing_account.id != self.instance.id):
            raise serializers.ValidationError("Account with this Owner and Name already exists.")
        
        return value
    
