
import pytest

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from wallets.models import Wallet
from wallets.tests.wallet.test_fixture import test_user


@pytest.mark.django_db
def test_wallet_update(test_user):

    # Create a wallet for the user
    wallet = Wallet.objects.create(name='Test Wallet', description='This is a test wallet', owner=test_user[0])

    assert Wallet.objects.count() == 1

    # Update the wallet
    wallet.name = 'Updated Wallet'
    wallet.description = 'This is an updated wallet'
    wallet.save()

    # Retrieve the wallet from the database. Look by id

    wallet = Wallet.objects.get(id=wallet.id)

    # Check the attributes of the wallet
    assert wallet.name == 'Updated Wallet'
    assert wallet.description == 'This is an updated wallet'

    # Check that the updated_at attribute has been updated
    assert wallet.created_at is not None
    assert wallet.updated_at is not None
    assert wallet.created_at != wallet.updated_at
    assert timezone.now() - wallet.updated_at < timezone.timedelta(seconds=1.5)
    assert wallet.owner == test_user[0]
    assert wallet.co_owners.count() == 0

@pytest.mark.django_db
def test_wallet_update_multiple_owners(test_user):

    # Create a wallet for the user
    wallet = Wallet.objects.create(name='Test Wallet', description='This is a test wallet', owner=test_user[0])

    # Add a second owner to the wallet
    wallet.co_owners.add(test_user[1])
    wallet.co_owners.add(test_user[2])

    assert Wallet.objects.count() == 1

    # Update the wallet
    wallet.name = 'Updated Wallet'
    wallet.description = 'This is an updated wallet'
    wallet.save()

    # Retrieve the wallet from the database. Look by id
    wallet = Wallet.objects.get(id=wallet.id)

    # Check the attributes of the wallet
    assert wallet.name == 'Updated Wallet'
    assert wallet.description == 'This is an updated wallet'

    # Check that the updated_at attribute has been updated
    assert wallet.created_at is not None
    assert wallet.updated_at is not None
    assert wallet.created_at != wallet.updated_at
    assert timezone.now() - wallet.updated_at < timezone.timedelta(seconds=1.5)
    assert wallet.owner == test_user[0]
    assert wallet.co_owners.count() == 2

@pytest.mark.django_db
def test_wallet_update_delete_co_owners(test_user):
    
        # Create a wallet for the user
        wallet = Wallet.objects.create(name='Test Wallet', description='This is a test wallet', owner=test_user[0])
    
        # Add a second owner to the wallet
        wallet.co_owners.add(test_user[1])
    
        assert Wallet.objects.count() == 1
        assert wallet.co_owners.count() == 1
    
        # Update the wallet
        wallet.name = 'Updated Wallet'
        wallet.description = 'This is an updated wallet'
        wallet.co_owners.remove(test_user[1])
        wallet.save()
    
        # Retrieve the wallet from the database. Look by id
        wallet = Wallet.objects.get(id=wallet.id)
    
        # Check the attributes of the wallet
        assert wallet.name == 'Updated Wallet'
        assert wallet.description == 'This is an updated wallet'
    
        # Check that the updated_at attribute has been updated
        assert wallet.created_at is not None
        assert wallet.updated_at is not None
        assert wallet.created_at != wallet.updated_at
        assert timezone.now() - wallet.updated_at < timezone.timedelta(seconds=1.5)
        assert wallet.owner == test_user[0]
        assert wallet.co_owners.count() == 0

@pytest.mark.django_db
def test_wallet_update_no_owner(test_user):
    
    check_wallet_validations(
        name='Test Wallet',
        owner=None,
        co_ownerss=None,
        description='This is a test wallet',
        error_field='owner',
        error_message='Wallet has no owner.',
        test_users=test_user
    )

@pytest.mark.django_db
def test_wallet_update_no_name(test_user):

    check_wallet_validations(
        name=None,
        owner=test_user[0],
        co_ownerss=None,
        description='This is a test wallet',
        error_field='name',
        error_message="['This field cannot be null.']",
        test_users=test_user
    )

@pytest.mark.django_db
def test_wallet_update_too_long_name(test_user):
         
        check_wallet_validations(
            name='A'*101,
            owner=test_user[0],
            co_ownerss=None,
            description='This is a test wallet',
            error_field='name',
            error_message="['Ensure this value has at most 100 characters (it has 101).']",
            test_users=test_user
        )

@pytest.mark.django_db
def test_wallet_update_too_short_name(test_user):
    
    check_wallet_validations(
        name='A',
        owner=test_user[0],
        co_ownerss=None,
        description='This is a test wallet',
        error_field='name',
        error_message="['Name must be at least 3 characters long']",
        test_users=test_user
    )

@pytest.mark.django_db
def test_wallet_update_duplicated_name(test_user):

    # Create a wallet for the user
    Wallet.objects.create(name='Test Wallet 2', description='This is a test wallet', owner=test_user[0])

    check_wallet_validations(
        name='Test Wallet 2',
        owner=test_user[0],
        co_ownerss=None,
        description='This is a test wallet',
        error_field='__all__',
        error_message="['Wallet with this Owner and Name already exists.']",
        test_users=test_user,
        other_wallets=1
    )

@pytest.mark.django_db
def test_wallet_update_too_long_description(test_user):

    check_wallet_validations(
        name='Test Wallet',
        owner=test_user[0],
        co_ownerss=None,
        description='A'*1001,
        error_field='description',
        error_message="['Ensure this value has at most 1000 characters (it has 1001).']",
        test_users=test_user
    )

@pytest.mark.django_db
def test_wallet_update_co_owners_same_as_owner(test_user):
        
        check_wallet_validations(
            name='Test Wallet',
            owner=test_user[0],
            co_ownerss=[test_user[0]],
            description='This is a test wallet',
            error_field='__all__',
            error_message="['The owner and co-owner must be different users']",
            test_users=test_user
        )

def check_wallet_validations(name, owner, co_ownerss, description, error_field, error_message, test_users, other_wallets = 0):
   
    # Create a wallet for the user

    wallet = Wallet.objects.create(name='Test Wallet', description='This is a test wallet', owner=test_users[0])

    assert Wallet.objects.count() == 1 + other_wallets

    with pytest.raises((ValidationError, Wallet.owner.RelatedObjectDoesNotExist)) as exception_info:

        wallet.name = name
        wallet.owner = owner
        if co_ownerss is not None:
            wallet.co_owners.set(co_ownerss)
        wallet.description = description
        wallet.save()

    try:
        errors = exception_info.value.error_dict[error_field]

        assert error_field in str(exception_info.value)
        assert len(errors) > 0
        assert str(errors[0]) == error_message
        assert Wallet.objects.count() == other_wallets + 1
    
    except AttributeError:
        assert error_message in str(exception_info.value)
        
    wallet = Wallet.objects.get(id=wallet.id)

    assert wallet.name == 'Test Wallet'
    assert wallet.owner == test_users[0]
    
    if co_ownerss is not None:
        assert wallet.co_owners.count() == len(co_ownerss)
    else:
        assert wallet.co_owners.count() == 0
    
    assert wallet.description == 'This is a test wallet'
