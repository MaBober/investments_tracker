import pytest

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Count


from wallets.models import Wallet, Account, Deposit

from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution

@pytest.mark.django_db
def test_deposit_update(test_user, test_currencies, test_wallets, test_accounts, test_account_types, test_account_institution_types, test_institution):

    # Create a deposit
    deposit = Deposit.objects.create(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=1000.00,
        currency=test_currencies[0],
        description='Initial deposit',
        deposited_at=timezone.now()
    )

    # Check that a Deposit object has been added to the database
    assert Deposit.objects.count() == 1

    # Retrieve the deposit from the database
    deposit = Deposit.objects.first()

    # Check the attributes of the deposit
    assert deposit.wallet == test_wallets[0]
    assert deposit.account == test_accounts[0]
    assert deposit.user == test_user[0]
    assert deposit.amount == 1000.00
    assert deposit.currency == test_currencies[0]
    assert deposit.description == 'Initial deposit'
    assert deposit.deposited_at is not None
    assert deposit.created_at is not None
    assert deposit.updated_at is not None
    assert deposit.created_at == deposit.updated_at
    assert timezone.now() - deposit.created_at < timezone.timedelta(seconds=1.5)

    # Update the deposit
    deposit.amount = 2000.00
    deposit.description = 'Updated deposit'
    deposit.save()

    # Retrieve the deposit from the database
    deposit = Deposit.objects.first()

    # Check the attributes of the deposit
    assert deposit.wallet == test_wallets[0]
    assert deposit.account == test_accounts[0]
    assert deposit.user == test_user[0]
    assert deposit.amount == 2000.00
    assert deposit.currency == test_currencies[0]
    assert deposit.description == 'Updated deposit'
    assert deposit.deposited_at is not None
    assert deposit.created_at is not None
    assert deposit.updated_at is not None
    assert deposit.created_at != deposit.updated_at

    assert timezone.now() - deposit.created_at < timezone.timedelta(seconds=1.5)
    assert Deposit.objects.count() == 1

    new_user =test_user[1]
    new_wallet = new_user.wallets.first()
    new_account = new_wallet.accounts.first()
    new_currency = new_account.currency

    # Update the deposit
    deposit.amount = 3000.00
    deposit.wallet = new_user.wallets.first()
    deposit.user = new_user
    deposit.account = new_wallet.accounts.first()
    deposit.currency = new_currency
    deposit.description = 'Updated deposit 2'
    deposit.save()

    # Retrieve the deposit from the database
    deposit = Deposit.objects.first()

    # Check the attributes of the deposit
    assert deposit.wallet == new_wallet
    assert deposit.account == new_account
    assert deposit.user == new_user
    assert deposit.amount == 3000.00
    assert deposit.currency == new_currency
    assert deposit.description == 'Updated deposit 2'
    assert deposit.deposited_at is not None
    assert deposit.created_at is not None
    assert deposit.updated_at is not None
    assert deposit.created_at != deposit.updated_at
    assert timezone.now() - deposit.updated_at < timezone.timedelta(seconds=1.5)

    assert Deposit.objects.count() == 1

    

@pytest.mark.django_db
def test_deposit_update_no_wallet(test_user, test_currencies, test_wallets, test_accounts, test_account_types, test_account_institution_types, test_institution):

    check_deposit_validations(
        wallet=None,
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now(),
        error_field='wallet',
        error_message='Deposit has no wallet.',
        fixture = {
            'users': test_user,
            'currencies': test_currencies,
            'wallets': test_wallets,
            'accounts': test_accounts,
            'account_types': test_account_types,
            'account_institution_types': test_account_institution_types,
            'institution': test_institution
        }
    )

@pytest.mark.django_db
def test_deposit_update_no_account(test_user, test_currencies, test_wallets, test_accounts, test_account_types, test_account_institution_types, test_institution):

    check_deposit_validations(
        wallet=test_wallets[0],
        account=None,
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now(),
        error_field='account',
        error_message='Deposit has no account.',
        fixture = {
            'users': test_user,
            'currencies': test_currencies,
            'wallets': test_wallets,
            'accounts': test_accounts,
            'account_types': test_account_types,
            'account_institution_types': test_account_institution_types,
            'institution': test_institution
        }
    )

@pytest.mark.django_db
def test_deposit_update_no_user(test_user, test_currencies, test_wallets, test_accounts, test_account_types, test_account_institution_types, test_institution):

    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=None,
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now(),
        error_field='user',
        error_message="Deposit has no user.",
        fixture = {
            'users': test_user,
            'currencies': test_currencies,
            'wallets': test_wallets,
            'accounts': test_accounts,
            'account_types': test_account_types,
            'account_institution_types': test_account_institution_types,
            'institution': test_institution
        }
    )

@pytest.mark.django_db
def test_deposit_update_no_amount(test_user, test_currencies, test_wallets, test_accounts, test_account_types, test_account_institution_types, test_institution):

    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=None,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now(),
        error_field='amount',
        error_message=['This field cannot be null.'],
        fixture = {
            'users': test_user,
            'currencies': test_currencies,
            'wallets': test_wallets,
            'accounts': test_accounts,
            'account_types': test_account_types,
            'account_institution_types': test_account_institution_types,
            'institution': test_institution
        }
    )

@pytest.mark.django_db
def test_deposit_update_no_currency(test_user, test_currencies, test_wallets, test_accounts, test_account_types, test_account_institution_types, test_institution):

    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=None,
        description='This is a test deposit',
        deposited_at=timezone.now(),
        error_field='currency',
        error_message="Deposit has no currency.",
        fixture = {
            'users': test_user,
            'currencies': test_currencies,
            'wallets': test_wallets,
            'accounts': test_accounts,
            'account_types': test_account_types,
            'account_institution_types': test_account_institution_types,
            'institution': test_institution
        }
    )

@pytest.mark.django_db
def test_deposit_update_too_long_description(test_user, test_currencies, test_wallets, test_accounts, test_account_types, test_account_institution_types, test_institution):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='A' * 1001,
        deposited_at=timezone.now(),
        error_field='description',
        error_message=['Ensure this value has at most 1000 characters (it has 1001).'],
        fixture = {
            'users': test_user,
            'currencies': test_currencies,
            'wallets': test_wallets,
            'accounts': test_accounts,
            'account_types': test_account_types,
            'account_institution_types': test_account_institution_types,
            'institution': test_institution
        }
    )

@pytest.mark.django_db
def test_deposit_update_no_deposited_at(test_user, test_currencies, test_wallets, test_accounts, test_account_types, test_account_institution_types, test_institution):

    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=None,
        error_field='deposited_at',
        error_message=['This field cannot be null.'],
        fixture = {
            'users': test_user,
            'currencies': test_currencies,
            'wallets': test_wallets,
            'accounts': test_accounts,
            'account_types': test_account_types,
            'account_institution_types': test_account_institution_types,
            'institution': test_institution
        }
    )

@pytest.mark.django_db
def test_deposit_update_future_deposited_at(test_user, test_currencies, test_wallets, test_accounts, test_account_types, test_account_institution_types, test_institution):

    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() + timezone.timedelta(days=1),
        error_field='deposited_at',
        error_message=['Date cannot be in the future.'],
        fixture = {
            'users': test_user,
            'currencies': test_currencies,
            'wallets': test_wallets,
            'accounts': test_accounts,
            'account_types': test_account_types,
            'account_institution_types': test_account_institution_types,
            'institution': test_institution
        }
    )

@pytest.mark.django_db
def test_deposit_update_negative_amount(test_user, test_currencies, test_wallets, test_accounts, test_account_types, test_account_institution_types, test_institution):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=-100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now(),
        error_field='amount',
        error_message=['Ensure this value is greater than or equal to 0.01.'],
        fixture = {
            'users': test_user,
            'currencies': test_currencies,
            'wallets': test_wallets,
            'accounts': test_accounts,
            'account_types': test_account_types,
            'account_institution_types': test_account_institution_types,
            'institution': test_institution
        }
    )

#TODO: Write down all possibilities of errors regarding wallet and account ownership
@pytest.mark.django_db
def test_deposit_with_currency_not_in_account(test_user, test_currencies, test_wallets, test_accounts, test_account_types, test_account_institution_types, test_institution):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[1],
        description='This is a test deposit',
        deposited_at=timezone.now(),
        error_field='__all__',
        error_message=['The currency of the deposit must be the same as the currency of the account.'],
        fixture = {
            'users': test_user,
            'currencies': test_currencies,
            'wallets': test_wallets,
            'accounts': test_accounts,
            'account_types': test_account_types,
            'account_institution_types': test_account_institution_types,
            'institution': test_institution
        }
    )
    

@pytest.mark.django_db
def test_deposit_update_zero_amount(test_user, test_currencies, test_wallets, test_accounts, test_account_types, test_account_institution_types, test_institution):
    
        check_deposit_validations(
            wallet=test_wallets[0],
            account=test_accounts[0],
            user=test_user[0],
            amount=0.00,
            currency=test_currencies[0],
            description='This is a test deposit',
            deposited_at=timezone.now(),
            error_field='amount',
            error_message=['Ensure this value is greater than or equal to 0.01.'],
            fixture = {
                'users': test_user,
                'currencies': test_currencies,
                'wallets': test_wallets,
                'accounts': test_accounts,
                'account_types': test_account_types,
                'account_institution_types': test_account_institution_types,
                'institution': test_institution
            }
        )

def check_deposit_validations(wallet, account, user, amount, currency, description, deposited_at, error_field, error_message, fixture):

    new_deposit = Deposit.objects.create(
        wallet=fixture['wallets'][0],
        account=fixture['accounts'][0],
        user=fixture['users'][0],
        amount=1000.00,
        currency=fixture['currencies'][0],
        description='Initial deposit',
        deposited_at=timezone.now()
    )
         

    with pytest.raises((ValidationError, Deposit.account.RelatedObjectDoesNotExist, Deposit.wallet.RelatedObjectDoesNotExist, Deposit.user.RelatedObjectDoesNotExist, Deposit.currency.RelatedObjectDoesNotExist )) as exception_info:
        new_deposit.wallet = wallet
        new_deposit.account = account
        new_deposit.user = user
        new_deposit.amount = amount
        new_deposit.currency = currency
        new_deposit.description = description
        new_deposit.deposited_at = deposited_at
        new_deposit.save()

    try:
        assert exception_info.value.message_dict[error_field] == error_message

    except AttributeError:
        assert error_message in str(exception_info.value)
