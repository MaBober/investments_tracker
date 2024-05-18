import pytest

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from wallets.models import Wallet
from wallets.tests.test_fixture import test_user


@pytest.mark.django_db
def test_wallet_delete_no_co_owners(test_user):
    
    # Create a wallet for the user
    wallet = Wallet.objects.create(name='Test Wallet', description='This is a test wallet', owner=test_user[0])

    assert Wallet.objects.count() == 1

    # Delete the wallet
    wallet.delete()

    # Check that the wallet has been deleted
    assert Wallet.objects.count() == 0

    # Check that the wallet has been deleted
    with pytest.raises(Wallet.DoesNotExist):
        wallet = Wallet.objects.get(id=wallet.id)
        assert wallet is None


@pytest.mark.django_db
def test_wallet_delete_multiple_owners(test_user):
        
    # Create a wallet for the user
    wallet = Wallet.objects.create(name='Test Wallet', description='This is a test wallet', owner=test_user[0])

    # Add a second owner to the wallet
    wallet.co_owners.add(test_user[1])
    wallet.co_owners.add(test_user[2])

    assert Wallet.objects.count() == 1

    # Delete the wallet
    wallet.delete()

    # Check that the wallet has been deleted
    assert Wallet.objects.count() == 0

    # Check that the wallet has been deleted
    with pytest.raises(Wallet.DoesNotExist):
        wallet = Wallet.objects.get(id=wallet.id)
        assert wallet is None

@pytest.mark.django_db
def test_wallet_delete_does_not_exist():

    # Try to delete a wallet that doesn't exist
    with pytest.raises(Wallet.DoesNotExist):
        wallet = Wallet.objects.get(id=999)
        wallet.delete()

@pytest.mark.django_db
def test_wallet_delete_removes_from_owner(test_user):
    
    # Create a wallet for the user
    wallet = Wallet.objects.create(name='Test Wallet', description='This is a test wallet', owner=test_user[0])

    assert wallet in test_user[0].wallets.all()

    # Delete the wallet
    wallet.delete()

    # Check that the wallet has been removed from the owner's wallets
    assert wallet not in test_user[0].wallets.all()


