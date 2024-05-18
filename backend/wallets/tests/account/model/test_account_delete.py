import pytest

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from wallets.models import Wallet, Account, AccountType, AccountInstitution, AccountInstitutionType
from wallets.tests.test_fixture import test_countries, test_currencies, test_user
from wallets.tests.account.test_fixture import test_account_types, test_account_institution_types, test_institution, test_accounts
from wallets.tests.wallet.test_fixture import test_wallets


@pytest.mark.django_db
def test_account_delete_no_wallet(test_accounts):
    
    # Delete the account
    account = test_accounts[0]
    account.wallets.clear()
    account.save()

    assert account.wallets.count() == 0

    account.delete()

    # Check that the account has been deleted
    with pytest.raises(Account.DoesNotExist):
        account = Account.objects.get(id=account.id)
        print(account)
        assert account is None

@pytest.mark.django_db
def test_account_delete_with_wallet(test_accounts, test_wallets):
    
    # Assign the account to the wallet
    account = test_accounts[0]
    wallet = test_wallets[0]
    
    account.wallets.add(wallet)
    wallet_accounts_amount = wallet.accounts.count()
    account.save()

    assert account.wallets.count() != 0

    # Delete the account
    account.delete()

    # Check that the account has been deleted
    with pytest.raises(Account.DoesNotExist):
        account = Account.objects.get(id=account.id)
        assert account is None

    # Check that the account has been removed from the wallet
    wallet.refresh_from_db()
    assert wallet.accounts.count() == wallet_accounts_amount-1
    assert wallet.accounts.filter(id=account.id).count() == 0
    assert wallet.accounts.filter(id=account.id).exists() == False
    assert wallet.accounts.filter(id=account.id).first() == None
    assert wallet.accounts.filter(id=account.id).last() == None

@pytest.mark.django_db
def test_account_delete_does_not_exist():
        
    # Try to delete an account that doesn't exist
    with pytest.raises(Account.DoesNotExist):
        account = Account.objects.get(id=999)
        account.delete()
        assert account is None

@pytest.mark.django_db
def test_account_delete_removes_from_owner(test_accounts, test_wallets):
        
        # Assign the account to the wallet
        account = test_accounts[0]
        wallet = test_wallets[0]

        owner = account.owner
        
        account.wallets.add(wallet)
        wallet_accounts_amount = wallet.accounts.count()
        account.save()
    
        assert account in account.owner.accounts.all()
    
        # Delete the account
        account.delete()
    
        # Check that the account has been removed from the owner's accounts
        assert account not in owner.accounts.all()