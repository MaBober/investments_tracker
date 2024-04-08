import pytest

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from wallets.models import Wallet
from wallets.tests.wallet.test_fixture import test_user



@pytest.mark.django_db
def test_wallet_create_single_owner(test_user):
    
    # Create a wallet for the user
    Wallet.objects.create(name='Test Wallet', description='This is a test wallet', owner=test_user[0])
    
    # Check that a Wallet object has been added to the database
    assert Wallet.objects.count() == 1

    # Retrieve the wallet from the database
    wallet = Wallet.objects.first()

    # Check the attributes of the wallet
    assert wallet.name == 'Test Wallet'
    assert wallet.description == 'This is a test wallet'
    assert wallet.owner == test_user[0]
    assert wallet.co_owners.count() == 0
    assert wallet.created_at is not None
    assert wallet.updated_at is not None
    assert wallet.created_at == wallet.updated_at
    assert timezone.now() - wallet.created_at < timezone.timedelta(seconds=1.5)

@pytest.mark.django_db
def test_wallet_create_multiple_owners(test_user):
    
        # Create a wallet for the user
        wallet = Wallet.objects.create(name='Test Wallet', description='This is a test wallet', owner=test_user[0])
    
        # Add a second owner to the wallet
        wallet.co_owners.add(test_user[1])
    
        # Check that a Wallet object has been added to the database
        assert Wallet.objects.count() == 1
    
        # Retrieve the wallet from the database
        wallet = Wallet.objects.first()
    
        # Check the attributes of the wallet
        assert wallet.name == 'Test Wallet'
        assert wallet.description == 'This is a test wallet'
        assert wallet.owner == test_user[0]
        assert wallet.co_owners.count() == 1

@pytest.mark.django_db
def test_wallet_create_no_owner(test_user):
        
        check_wallet_validations(
            name='Test Wallet',
            owner=None,
            co_owners=None,
            description='This is a test wallet',
            error_field='owner',
            error_message="['This field cannot be null.']"
        )

@pytest.mark.django_db
def test_wallet_create_no_name(test_user):

    check_wallet_validations(
        name=None,
        owner=test_user[0],
        co_owners=None,
        description='This is a test wallet',
        error_field='name',
        error_message="['This field cannot be null.']"
    )

@pytest.mark.django_db
def test_wallet_create_too_short_name(test_user):

    check_wallet_validations(
        name='A',
        owner=test_user[0],
        co_owners=None,
        description='This is a test wallet',
        error_field='name',
        error_message="['Name must be at least 3 characters long']"
    )

@pytest.mark.django_db
def test_wallet_create_duplicated_name(test_user):
         
        # Create a wallet for the user
        Wallet.objects.create(name='Test Wallet', description='This is a test wallet', owner=test_user[0])

        assert Wallet.objects.count() == 1
    
        check_wallet_validations(
            name='Test Wallet',
            owner=test_user[0],
            co_owners=None,
            description='This is a test wallet',
            error_field='__all__',
            error_message="['Wallet with this Owner and Name already exists.']",
            other_wallets=1
        )

@pytest.mark.django_db
def test_wallet_create_too_long_name(test_user):

    check_wallet_validations(
        name='A' * 101,
        owner=test_user[0],
        co_owners=None,
        description='This is a test wallet',
        error_field='name',
        error_message="['Ensure this value has at most 100 characters (it has 101).']"
    )

@pytest.mark.django_db
def test_wallet_create_too_long_description(test_user):

    check_wallet_validations(
        name='Test Wallet',
        owner=test_user[0],
        co_owners=None,
        description='A' * 1001,
        error_field='description',
        error_message="['Ensure this value has at most 1000 characters (it has 1001).']"
    )

@pytest.mark.xfail
@pytest.mark.django_db
def test_wallet_owner_same_as_co_owner(test_user):
         
        check_wallet_validations(
            name='Test Wallet',
            owner=test_user[0],
            co_owners=[test_user[0]],
            description='This is a test wallet',
            error_field='__all__',
            error_message="['The owner and co-owner must be different users']"
        )     


def check_wallet_validations(name, owner, co_owners, description, error_field, error_message, other_wallets = 0):
   
    with pytest.raises(ValidationError) as exception_info:
        Wallet.objects.create(name=name, owner=owner, description=description)

    assert Wallet.objects.count() == other_wallets
    errors = exception_info.value.error_dict[error_field]

    assert error_field in str(exception_info.value)
    assert len(errors) > 0
    assert str(errors[0]) == error_message
    
    # Check that a Wallet object has not been added to the database
    assert Wallet.objects.count() == other_wallets