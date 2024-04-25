import pytest

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone
from django.db.models import Count


from wallets.models import Wallet, Account, Deposit

from wallets.tests.test_fixture import test_user, test_currencies, test_countries
from wallets.tests.wallet.test_fixture import test_wallets
from wallets.tests.account.test_fixture import test_accounts, test_account_types, test_account_institution_types, test_institution

@pytest.mark.django_db
def test_deposit_create(test_user, test_wallets, test_accounts, test_currencies):

    current_time = timezone.now()
    # Create a deposit for the account
    Deposit.objects.create(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=current_time - timezone.timedelta(days=1)
    )

    # Check that a Deposit object has been added to the database
    assert Deposit.objects.count() == 1

    # Retrieve the deposit from the database
    deposit = Deposit.objects.first()

    # Check the attributes of the deposit
    assert deposit.wallet == test_wallets[0]
    assert deposit.account == test_accounts[0]
    assert deposit.user == test_user[0]
    assert deposit.amount == 100.00
    assert deposit.currency == test_currencies[0]
    assert deposit.description == 'This is a test deposit'
    assert deposit.deposited_at is not None
    assert deposit.created_at is not None
    assert deposit.updated_at is not None
    assert deposit.created_at == deposit.updated_at
    assert timezone.now() - deposit.created_at < timezone.timedelta(seconds=1.5)
    assert deposit.deposited_at == current_time - timezone.timedelta(days=1)

@pytest.mark.django_db
def test_deposit_create_no_wallet(test_user, test_accounts, test_currencies):
    
    check_deposit_validations(
        wallet=None,
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='wallet',
        error_message='Deposit has no wallet.'
    )

@pytest.mark.django_db
def test_deposit_create_no_account(test_user, test_wallets, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=None,
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='account',
        error_message='Deposit has no account.'
    )

@pytest.mark.django_db
def test_deposit_create_no_user(test_accounts, test_wallets, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=None,
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='user',
        error_message='Deposit has no user.'
    )

@pytest.mark.django_db
def test_deposit_create_no_amount(test_user, test_wallets, test_accounts, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=None,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='amount',
        error_message='This field cannot be null.'
    )

@pytest.mark.django_db
def test_deposit_create_no_currency(test_user, test_wallets, test_accounts):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=None,
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='currency',
        error_message='Deposit has no currency.'
    )

@pytest.mark.django_db
def test_deposit_create_with_currency_not_in_db(test_user, test_wallets, test_accounts):

    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency='XYZ',
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='currency',
        error_message='Cannot assign "\'XXX\'": "Deposit.currency" must be a "Currency" instance.'
    )

@pytest.mark.django_db
def test_deposit_create_with_currency_not_in_account(test_user, test_wallets, test_accounts, test_currencies):

    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[1],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='currency',
        error_message='The currency of the deposit must be the same as the currency of the account.'
    )

@pytest.mark.django_db
def test_deposit_create_too_long_description(test_user, test_wallets, test_accounts, test_currencies):

    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='a' * 1001,
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='description',
        error_message='Ensure this value has at most 1000 characters (it has 1001).'
    )

@pytest.mark.django_db
def test_deposit_create_no_deposited_at(test_user, test_wallets, test_accounts, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=None,
        error_field='deposited_at',
        error_message='This field cannot be null.'
    )

@pytest.mark.django_db
def test_deposit_create_future_deposited_at(test_user, test_wallets, test_accounts, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() + timezone.timedelta(days=1),
        error_field='deposited_at',
        error_message='Date cannot be in the future.'
    )

@pytest.mark.django_db
def test_deposit_create_negative_amount(test_user, test_wallets, test_accounts, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=-100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='amount',
        error_message='Ensure this value is greater than or equal to 0.01.'
    )

@pytest.mark.django_db
def test_deposit_create_zero_amount(test_user, test_wallets, test_accounts, test_currencies):
    
    check_deposit_validations(
        wallet=test_wallets[0],
        account=test_accounts[0],
        user=test_user[0],
        amount=0,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='amount',
        error_message='Ensure this value is greater than or equal to 0.01.'
    )

#TODO: Write down all possibilities of errors regarding wallet and account ownership
@pytest.mark.django_db
def test_deposit_create_on_account_not_in_wallet(test_user, test_wallets, test_accounts, test_currencies):

    wallet = test_wallets[0]
    account = test_accounts[1]

    account.wallets.clear()
    account.save() 

    check_deposit_validations(
        wallet=wallet,
        account=account,
        user=test_user[0],
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='account',
        error_message='Account does not belong to the wallet.'
    )

@pytest.mark.django_db
def test_deposit_create_on_wallet_not_owned_by_user(test_user, test_wallets, test_accounts, test_currencies):
        
    user = test_user[1]
    wallet = test_wallets[1]
    account = test_accounts[1]

    account.wallets.clear()
    account.wallets.add(wallet)
    account.save()

    wallet.owner = test_user[0]
    wallet.co_owners.clear()
    wallet.save()


    check_deposit_validations(
        wallet=wallet,
        account=account,
        user=user,
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='unauthorized_deposit',
        error_message='The user must be the owner or a co-owner of the wallet to make a deposit.'
    )

@pytest.mark.django_db
def test_deposit_create_on_account_not_owned_by_user(test_user, test_wallets, test_accounts, test_currencies):
            
    user = test_user[1]
    wallet = test_wallets[1]
    account = test_accounts[1]

    account.wallets.clear()
    account.co_owners.clear()
    account.owner = test_user[2]    
    account.wallets.add(wallet)
    account.save()

    wallet.owner = test_user[1]
    wallet.co_owners.clear()
    wallet.save()

    check_deposit_validations(
        wallet=wallet,
        account=account,
        user=user,
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1),
        error_field='unauthorized_deposit',
        error_message='You are not authorized to make this deposit.'
    )

@pytest.mark.django_db
def test_deposit_on_wallet_co_owner(test_user, test_wallets, test_accounts, test_currencies):
    
        wallet = test_wallets[0]
        account = test_accounts[0]
        user = test_user[0]

        wallet.co_owners.clear()
        wallet.owner = test_user[1]
        wallet.co_owners.add(user)
        wallet.save()

        account.wallets.clear()
        account.wallets.add(wallet)
        account.save()
    
        Deposit.objects.create(
            wallet=wallet,
            account=account,
            user=user,
            amount=100.00,
            currency=test_currencies[0],
            description='This is a test deposit',
            deposited_at=timezone.now() - timezone.timedelta(days=1)
        )
    
        assert Deposit.objects.count() == 1
    
        deposit = Deposit.objects.first()
    
        assert deposit.wallet == wallet
        assert deposit.account == account
        assert deposit.user == user
        assert deposit.amount == 100.00
        assert deposit.currency == test_currencies[0]


@pytest.mark.django_db
def test_deposit_on_account_co_owner(test_user, test_wallets, test_accounts, test_currencies):
        
    wallet = test_wallets[0]
    account = test_accounts[0]
    user = test_user[0]

    account.co_owners.clear()
    account.owner = test_user[1]
    account.co_owners.add(user)
    account.save()

    wallet.owner = test_user[0]
    wallet.co_owners.clear()
    wallet.save()

    account.wallets.clear()
    account.wallets.add(wallet)
    account.save()

    Deposit.objects.create(
        wallet=wallet,
        account=account,
        user=user,
        amount=100.00,
        currency=test_currencies[0],
        description='This is a test deposit',
        deposited_at=timezone.now() - timezone.timedelta(days=1)
    )

    assert Deposit.objects.count() == 1

    deposit = Deposit.objects.first()

    assert deposit.wallet == wallet
    assert deposit.account == account
    assert deposit.user == user
    assert deposit.amount == 100.00
    assert deposit.currency == test_currencies[0]


def check_deposit_validations(wallet, account, user, amount, currency, description, deposited_at, error_field, error_message):

    with pytest.raises((ValidationError, ObjectDoesNotExist)) as exception_info:
        Deposit.objects.create(
            wallet=wallet,
            account=account,
            user=user,
            amount=amount,
            currency=currency,
            description=description,
            deposited_at=deposited_at 
        )

    try:
        assert exception_info.value.message_dict[error_field][0] == error_message
        assert Deposit.objects.count() == 0

    except AttributeError:
        assert error_message in str(exception_info.value)
        assert Deposit.objects.count() == 0

